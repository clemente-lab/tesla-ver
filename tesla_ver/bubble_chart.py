import base64
import io
from pathlib import Path
from functools import reduce


import dash
import pandas as pd
import numpy as np
from plotly.graph_objects import Scatter
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from tesla_ver.layout import LAYOUT


def generateBubbleChart(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/bubblechart.html/")
    app.layout = LAYOUT

    @app.callback(
        Output("hidden-data", "children"),
        [Input("upload", "contents"), Input("upload", "filename"), Input("upload", "last_modified"),],
    )
    def upload_data(list_of_contents, list_of_filenames, _):
        """This callback handles storing the dataframe as JSON in the hidden
        component."""

        def parse_contents(contents, filenames):
            """Parse a Dash Upload into a DataFrame.

            contents is a string read from the upload component.
            filename and date are just information paramteres
            """
            # Parses contents into dataframes
            df_list = list()
            filename_titles = list()
            for content, filename in zip(contents, filenames):
                _, content_string = content.split(",")
                # Append filename
                filename = Path(filename).stem
                filename_titles.append(filename)
                decoded = base64.b64decode(content_string)
                fileish = io.StringIO(decoded.decode("utf-8"))
                df = pd.read_csv(fileish, sep="\t")
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

        df = None
        if list_of_contents is not None:
            df = parse_contents(list_of_contents, list_of_filenames)
            return df.to_json()
        return

    @app.callback(
        [Output("time-slider", "marks"), Output("time-slider", "min"), Output("time-slider", "max"),],
        [Input("hidden-data", "children")],
    )
    def update_slider(data):
        """This callback updates the slider values from a hidden div containing trajectory data
        Data produced by upload_data callback function"""
        if data is None:
            raise PreventUpdate
        df = pd.read_json(data)
        time_min = df["X"].min()
        time_max = df["X"].max()
        marks = {str(year): {"label": str(year), "style": {"visibility": "hidden"}} for year in df["X"].unique()}
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
        [Input("hidden-data", "children"),],
    )
    def update_dropdowns(json_data):
        """This callback generates dictionaries of options for dropdown selection"""
        if json_data is None:
            raise PreventUpdate
        df = pd.read_json(json_data)
        data_columns = [title for title in df.select_dtypes(include=[np.number]).columns]
        data_options = [
            {"label": option.replace("_", " ").title(), "value": option}
            for option in data_columns
            if ("trajs" in option)
        ]
        size_options = [
            {"label": option.replace("_", " ").title(), "value": option}
            for option in [sizeopt for sizeopt in data_columns if ("trajs" not in sizeopt and sizeopt not in ["X"])]
        ]
        annotation_options = [
            {"label": option.replace("_", " ").title(), "value": option}
            for option in [anno for anno in df.columns if ("trajs" not in anno and anno not in ["ID", "X"])]
        ]
        return [
            data_options,
            data_options,
            size_options,
            annotation_options,
        ]

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
        [State("hidden-data", "children"), State("time-slider", "marks")],
    )
    def update_figure(
        _, time_value, y_column_name, x_column_name, size_dropdown_name, annotation_column_name, json_data, marks,
    ):
        """This callback handles updating the graph in response to user
        actions."""
        # Prevents updates without data
        if not all(
            val is not None
            for val in [json_data, size_dropdown_name, annotation_column_name, x_column_name, y_column_name,]
        ):
            raise PreventUpdate

        df = pd.read_json(json_data)
        traces = list()
        filtered_df = df[df["X"] == time_value].convert_dtypes()
        for entity in filtered_df["alpha-3"].unique():
            df_by_value = filtered_df[filtered_df["alpha-3"] == entity]
            traces.append(
                Scatter(
                    x=df_by_value[x_column_name],
                    y=df_by_value[y_column_name],
                    mode="markers",
                    opacity=0.9,
                    name=entity,
                    hovertext=df_by_value[annotation_column_name].values.tolist(),
                ),
            )

        figure = {
            "data": traces,
            "layout": dict(
                xaxis={"type": "log", "title": " ".join(x_column_name.split("_")).title(), "autorange": "true",},
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
