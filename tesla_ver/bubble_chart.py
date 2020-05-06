import base64
import io

import dash
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from tesla_ver.layout import LAYOUT


def generateBubbleChart(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/bubblechart.html/")
    app.layout = LAYOUT

    @app.callback(
        [
            Output("time-slider", "marks"),
            Output("time-slider", "min"),
            Output("time-slider", "max"),
        ],
        [Input("hidden-data", "children")],
    )
    def update_slider(data):
        if data is None:
            raise PreventUpdate
        df = pd.read_json(data)
        time_min = df["X"].min()
        time_max = df["X"].max()
        marks = {
            str(year): {"label": str(year), "style": {"visibility": "hidden"}}
            for year in df["X"].unique()
        }
        for key in list(marks.keys())[::5]:
            marks[key]["style"] = {"visibility": "visible"}
        return [marks, time_min, time_max]

    @app.callback(
        Output("hidden-data", "children"),
        [
            Input("upload", "contents"),
            Input("upload", "filename"),
            Input("upload", "last_modified"),
        ],
    )
    def upload_data(contents, filename, last_modified):
        """This callback handles storing the dataframe as JSON in the hidden
        component."""

        def parse_contents(contents):
            """Parse a Dash Upload into a DataFrame.

            contents is a string read from the upload component.
            filename and date are just information paramteres
            """
            _, content_string = contents.split(",")

            decoded = base64.b64decode(content_string)
            fileish = io.StringIO(decoded.decode("utf-8"))
            df = pd.read_csv(fileish, sep="\t")
            df[
                [
                    "X",
                    *[
                        column[0:-5]
                        for column in df.columns[0].split(",")
                        if column.endswith("_data")
                    ],
                ]
            ] = df[
                [
                    "X",
                    *[
                        column[0:-5]
                        for column in df.columns[0].split(",")
                        if column.endswith("_data")
                    ],
                ]
            ].applymap(
                lambda x: x.split(",")
            )
            df = df.apply(pd.Series.explode)
            df.reset_index(drop=True, inplace=True)
            return df

        df = None
        if contents is not None:
            df = parse_contents(contents).to_json()
        return df

    # @app.callback(
    #     Output("graph", "style"),
    #     [Input("upload-button", "n_clicks")],
    #     [State("hidden-data", "children")],
    # )
    # def display_graph(_, data):
    #     """Shows and hides the graph depending if data is uploaded."""
    #     if data is not None:
    #         return {"display": "flex"}
    #     return {"display": "none"}

    # @app.callback(
    #     [
    #         Output("y_dropdown", "options"),
    #         Output("x_dropdown", "options"),
    #         Output("size_dropdown", "options"),
    #         Output("annotation_dropdown", "options")
    #     ],
    #     [Input("hidden-data", "children"),],)
    # def update_dropdowns(json_data):
    #     if json_data is None:
    #         raise PreventUpdate
    #     df = pd.read_json(json_data)
    #     columns = df.select_dtypes(include=[np.number]).columns
    #     return [[{'label': option.replace('_',' ').title() ,'value': option} for option in columns] for dropdown in range(0,4)]

    # @app.callback(
    #     Output("graph-with-slider", "figure"),
    #     [
    #         Input("upload-button", "n_clicks"),
    #         Input("time-slider", "value"),
    #         Input("y_dropdown", "value"),
    #         Input("x_dropdown", "value"),
    #         Input("size_dropdown", "value"),
    #         Input("annotation_dropdown", "value"),
    #     ],
    #     [State("hidden-data", "children"), State('time-slider', 'marks')],
    # )
    # def update_figure(_, time_value, y_column_name, x_column_name,
    #                   size_dropdown_name,annotation_column_name,
    #                   json_data, marks):
    #     """This callback handles updating the graph in response to user
    #     actions."""
    #     if not all(val is not None for val in [json_data, size_dropdown_name,
    #                                        annotation_column_name, x_column_name, y_column_name]):
    #         raise PreventUpdate
    #     df = pd.read_json(json_data)
    #     traces = list()
    #     filtered_df = df[df["X"] == time_value]
    #     for entity in filtered_df.name.unique():
    #         df_by_value = filtered_df[filtered_df['name'] == entity]
    #         traces.append(
    #             go.scatter(
    #                 x = df_by_value[x_column_name],
    #                 y = df_by_value[y_column_name],
    #                 mode='markers',
    #                 opacity=0.9,
    #                 name=entity,
    #                 hovertext=df_by_value[annotation_column_name].values.tolist()
    #             ),
    #         )

    #     figure = {
    #         "data": traces,
    #         "layout": dict(
    #             xaxis={
    #             "type": "log",
    #             "title": " ".join(x_column_name.split("_")).title(),
    #             "autorange": "true",
    #         },
    #         yaxis={"title": " ".join(y_column_name.split("_")).title(), "autorange": "true",},
    #         margin={"l": 40, "b": 40, "t": 10, "r": 10},
    #         legend={"x": 0, "y": 1},
    #         hovermode="closest",
    #         # Defines transition behaviors
    #         transition={"duration": 500, "easing": "cubic-in-out"},
    #         )
    #     }

    #     return figure
    return app
