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
            df[["X", "Y"]] = df[["X", "Y"]].applymap(lambda x: x.split(","))
            df = df.apply(pd.Series.explode)
            df.reset_index(drop=True, inplace=True)
            return df
        df = None
        if contents is not None:
            df = parse_contents(contents).to_json()
        return df

    @app.callback(
        Output("graph", "style"),
        [Input("upload-button", "n_clicks")],
        [State("hidden-data", "children")],
    )
    def display_graph(_, data):
        """Shows and hides the graph depending if data is uploaded."""
        if data is not None:
            return {"display": "flex"}
        return {"display": "none"}

    @app.callback(
        [
            Output("y_dropdown", "options"),
            Output("x_dropdown", "options"),
            Output("size_dropdown", "options"),
            Output("annotation_dropdown", "options")
        ],
        Input("hidden-data", "children"))
    def update_dropdowns(json_data):
        if json_data is None:
            raise PreventUpdate
        df = pd.read_json(json_data)
        columns = df.select_dtypes(include=[np.number]).columns
        return [[{'label': option.replace('_',' ').title() ,'value': option} for option in columns] for dropdown in range(0,5)]

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
        [State("hidden-data", "children")],
    )
    def update_figure(
        _,
        annotation_column_name,
        json_data,
    ):
        """Returns graph data to figure."""
        if json_data is None:
            raise PreventUpdate
        df = pd.read_json(json_data)
        # Set default values for when no data has yet been loaded
        time_min = df["X"].min()
        time_max = df["X"].max()
        figure = dict()
        marks = {
                str(year): {"label": str(year), "style": {"visibility": "hidden"}}
                for year in df["X"].unique()
            }
        traces = list()
        return

    return app
