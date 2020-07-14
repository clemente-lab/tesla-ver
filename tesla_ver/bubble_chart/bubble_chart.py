import base64
import io
import dash
import json
import pdb

import pandas as pd
import numpy as np
import pyarrow as pa

from ast import literal_eval
from plotly.graph_objects import Scatter
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pathlib import Path
from functools import reduce

from tesla_ver.bubble_chart.bubble_chart_layout import LAYOUT
from tesla_ver.redis_manager import redis_manager


def generate_bubble_chart(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/bubblechart.html/")
    app.layout = LAYOUT

    @app.callback(
        [Output("df-data", "data"), Output("df-mdata", "data"), Output("graph", "style")],
        [Input("upload-button", "n_clicks"),],
    )
    def load_redis_data(n_clicks):
        if n_clicks == 0:
            raise PreventUpdate

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

        context = pa.default_serialization_context()
        df = context.deserialize(redis_manager.redis.get("data_numeric"))
        redis_manager.redis.flushdb()
        mdata = extract_mdata(df, "Year")
        df.rename(columns={"Year": "X"}, inplace=True)
        df = json.dumps({group_name: df_group.to_json() for group_name, df_group in df.groupby("X")})
        return [df, mdata, {"visibility": "visible"}]

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

        return [
            data_options,
            data_options,
            data_options,
            data_options,
        ]

    @app.callback(
        Output("graph-with-slider", "figure"),
        [
            Input("time-slider", "value"),
            Input("y_dropdown", "value"),
            Input("x_dropdown", "value"),
            Input("size_dropdown", "value"),
            Input("annotation_dropdown", "value"),
        ],
        [State("df-data", "data"), State("time-slider", "marks"), State("df-mdata", "data")],
    )
    def update_figure(
        time_value, y_column_name, x_column_name, size_dropdown_name, annotation_column_name, json_data, marks, mdata
    ):
        """This callback handles updating the graph in response to user
        actions."""
        # Prevents updates without data
        if None in [json_data, size_dropdown_name, annotation_column_name, x_column_name, y_column_name, mdata]:
            raise PreventUpdate

        if time_value == None:
            time_value = int(mdata.get("time_min"))

        df_by_time = pd.DataFrame.from_dict(literal_eval(json.loads(json_data).get(str(time_value))))

        scatterplot = Scatter(
            x=df_by_time[x_column_name],
            y=df_by_time[y_column_name],
            mode="markers",
            opacity=0.7,
            marker={"size": 15, "line": {"width": 0.5, "color": "white"}},
            hovertext=df_by_time["Subject"],
        )

        traces_data = list()
        traces_data.append(scatterplot)

        figure = {
            "data": traces_data,
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

    @app.callback(
        [Output("play-pause-button", "children"), Output("play-interval", "disabled")],
        [Input("play-pause-button", "n_clicks")],
    )
    def playPauseSwitch(n_clicks):
        if n_clicks % 2 == 0:
            return ["Pause", False]
        elif n_clicks % 2 != 0:
            return ["Play", True]

    @app.callback(
        Output("time-slider", "value"), [Input("play-interval", "n_intervals")], [State("time-slider", "value")]
    )
    def playIncrement(n_intervals, time_value):
        if time_value is None:
            raise PreventUpdate
        print(time_value)
        return str(int(time_value) + 1)

    return app
