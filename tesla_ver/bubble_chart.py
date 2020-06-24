import base64
import io
import dash
import pandas as pd
import numpy as np
import ast
from plotly.graph_objects import Scatter
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pathlib import Path
from functools import reduce

from tesla_ver.layout import LAYOUT


def generateBubbleChart(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/bubblechart.html/")
    app.layout = LAYOUT

    @app.callback(
        [Output("df-data", "data"), Output("df-mdata", "data")],
        [Input("upload", "contents"), Input("upload", "filename"), Input("upload", "last_modified"),],
    )
    def upload_data(list_of_contents, list_of_filenames, _):
        """This callback handles storing the dataframe as JSON in the data storage
        component."""

        df = None

        if None in [list_of_contents, list_of_filenames] or len(list_of_contents) != 1:
            raise PreventUpdate

        def upload_string_to_df(content):
            _, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            fileish = io.StringIO(decoded.decode("utf-8"))
            return pd.read_csv(fileish, sep="\t")

        def parse_multiple_contents(contents, filenames):
            """Parse a Dash Upload into a DataFrame.

            contents is a string read from the upload component.
            filename and date are just information paramteres
            """
            # Parses contents into dataframes
            df_list = list()
            filename_titles = list()
            for content, filename in zip(contents, filenames):
                df = upload_string_to_df(content)
                # Separates time series into a single value
                df[["X", "Y"]] = df[["X", "Y"]].applymap(lambda x: x.split(","))
                df = df.apply(pd.Series.explode)
                df.reset_index(drop=True, inplace=True)
                df = df.rename(columns={"Y": filename})
                df_list.append(df)

            # Merges all dataframes into a single list
            df = reduce(
                lambda left_frame, right_frame: pd.merge_ordered(
                    left_frame,
                    right_frame,
                    on=[column for column in left_frame.columns if column not in [*filename_titles]],
                    left_by="X",
                    fill_method="ffill",
                ),
                df_list,
            )
            df = df.convert_dtypes()
            df[filename_titles] = df[filename_titles].apply(pd.to_numeric, errors="coerce")
            df[df.select_dtypes(np.number).columns] = df[df.select_dtypes(np.number).columns].fillna(0)
            return df

        def extract_mdata(df, x_column_name):
            """Extracts dataframe metadata to make processing quicker and easier to debug

            Args:
                df (Dataframe): overall dataframe to extract metadata from
                x_column_name (str): name of column with time values
            Returns:
                dict: In the format of {time_max:int, time_min:int, x_vals:list(int), numeric_cols:list(str), mdata_cols:list(str)})

            """
            x_vals = sorted(df[x_column_name].unique())
            return {
                "time_min": min(x_vals),
                "time_max": max(x_vals),
                "x_vals": x_vals,
                "data_cols": [col for col in df.columns.values.tolist() if col not in ["X", "Year", "Subject"]],
            }


        
        df = upload_string_to_df(list_of_contents[0])
        mdata = extract_mdata(df, "Year")
        df.rename(columns={"Year": "X"}, inplace=True)
        df = json.dumps({group_name: df_group.to_json() for group_name, df_group in df.groupby("X")})
        return [df, mdata]

    @app.callback(
        [Output("time-slider", "marks"), Output("time-slider", "min"), Output("time-slider", "max"),],
        [Input("df-mdata", "modified_timestamp")],
        [State("df-mdata", "data")],
    )
    def update_slider(timestamp, mdata):
        """This callback updates the slider values from a storage component containing trajectory data
        Data produced by upload_data callback function"""
        if mdata is None:
            raise PreventUpdate
        time_min = int(mdata.get("time_min"))
        time_max = int(mdata.get("time_max"))
        # Generates a dictionary of slider marks, one for each time point.
        # All marks are styled to be hidden.  The loop below then makes some marks visible
        # an example mark for 1960 would look like {"1960":{"label":"1960","style":{"visiblitity":"hidden"}}}
        marks = {str(year): {"label": str(year), "style": {"visibility": "hidden"}} for year in mdata.get("x_vals")}
        # Changes the styling of every fourth mark to be visible for readablity
        # (time values overlap and become unreadable if every mark is shown)
        # Every fourth is just chosen for a balance of convenience and usability
        for idx, key in enumerate(marks.keys()):
            if idx % 4 == 0:
                marks[key]["style"] = {"visibility": "visible"}
        return [marks, time_min, time_max]

    @app.callback(
        [
            Output("y_dropdown", "options"),
            Output("x_dropdown", "options"),
            Output("size_dropdown", "options"),
            Output("annotation_dropdown", "options"),
        ],
        [Input("df-mdata", "modified_timestamp")],
        [State("df-mdata", "data")],
    )
    def update_dropdowns(timestamp, mdata):
        """This callback generates dictionaries of options for dropdown selection

        Args:
            timestamp (timestamp): timestamp to capture data updates
            json_data (json string): json string for the metadata

        Raises:
            PreventUpdate: prevents update for initial callback

        Returns:
            dict: dictionaries of options that populate dcc.Dropdown's
        """
        if mdata is None:
            raise PreventUpdate
        data_options = [
            {"label": option.replace("_", " ").title(), "value": option} for option in mdata.get("data_cols")
        ]
        # data_columns = [title for title in df.select_dtypes(include=[np.number]).columns]
        # data_options = [
        #     {"label": option.replace("_", " ").title(), "value": option}
        #     for option in data_columns
        #     if ("trajs" in option)
        # ]
        # size_options = [
        #     {"label": option.replace("_", " ").title(), "value": option}
        #     for option in [sizeopt for sizeopt in data_columns if ("trajs" not in sizeopt and sizeopt not in ["X"])]
        # ]
        # annotation_options = [
        #     {"label": option.replace("_", " ").title(), "value": option}
        #     for option in [anno for anno in df.columns if ("trajs" not in anno and anno not in ["ID", "X"])]
        # ]
        return [
            data_options,
            data_options,
            data_options,
            data_options,
        ]

    # Update figure still needs to be refactored, but other callbacks are optimized with seperate mdata dictionary
    @app.callback(
        Output("graph-with-slider", "figure"),
        [
            Input("upload-button", "n_clicks"),
            Input("time-slider", "value"),
            Input("y_dropdown", "value"),
            Input("x_dropdown", "value"),
            Input("size_dropdown", "value"),
            Input("annotation_dropdown", "value"),
        ],
        [State("df-data", "data"), State("time-slider", "marks")],
    )
    def update_figure(
        _, time_value, y_column_name, x_column_name, size_dropdown_name, annotation_column_name, json_data, marks,
    ):
        """This callback handles updating the graph in response to user
        actions."""
        # Prevents updates without data
        if None in [
            json_data,
            size_dropdown_name,
            annotation_column_name,
            x_column_name,
            y_column_name,
        ]:
            raise PreventUpdate

        df_by_time = pd.DataFrame.from_dict(ast.literal_eval(json.loads(json_data).get(str(time_value))))

        # splot = Scattergl(
        #     x=df_by_value[x_column_name],
        #     y=df_by_value[y_column_name],
        #     mode="markers",
        #     opacity=0.9,
        #     size=15
        #     name=df_by_time,
        #     hovertext=df_by_value[annotation_column_name].values.tolist(),
        # )

        # scatterplot = Scatter(
        #     x=df_by_time[x_column_name],
        #     y=df_by_time[y_column_name],
        #     mode="markers",
        #     opacity=0.9,
        #     # size=15,
        #     hovertext=df_by_time["Subject"],
        # )

        figure = {
            "data": [
                dict(
                    x=df_by_time[x_column_name],
                    y=df_by_time[y_column_name],
                    text=df_by_time["Subject"],
                    mode="markers",
                    marker={"size": 15, "opacity": 0.5, "line": {"width": 0.5, "color": "white"}},
                )
            ],
            "layout": dict(
                xaxis={"title": " ".join(x_column_name.split("_")).title(), "autorange": "true",},
                yaxis={"title": " ".join(y_column_name.split("_")).title(), "autorange": "true",},
                margin={"l": 40, "b": 40, "t": 10, "r": 10},
                legend={"x": 0, "y": 1},
                hovermode="closest",
                # Defines transition behaviors
                transition={"duration": 500, "easing": "cubic-in-out"},
            ),
        }

        return figure

    return app
