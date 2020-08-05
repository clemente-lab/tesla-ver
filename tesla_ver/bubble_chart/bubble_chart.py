import base64
import io
import dash
import json
import logging

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
    logging.debug("Bubble Chart app created")

    app.layout = LAYOUT
    logging.debug("Bubble Chart layout created")

    @app.callback(
        [Output("df-data", "data"), Output("df-mdata", "data"), Output("graph", "style")],
        [Input("upload-button", "n_clicks"),],
    )
    def load_redis_data(n_clicks):
        if n_clicks == 0:
            logging.debug("Bubble Chart Load Data Initial State Set")
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
                "ranges": {
                    col: (min(df[col]) * 1.25, max(df[col] * 1.25))
                    for col in df.columns.values.tolist()
                    if col not in ["X", "Year", "Subject"]
                },
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
        logging.debug(f"✅ Marks Dictionary Created, time values are: {marks.keys()}")
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

        logging.debug(f'✅ Data Options created, values are {mdata.get("data_cols")}')

        return [
            data_options,
            data_options,
            data_options,
            data_options,
        ]

    @app.callback(
        Output("bubble-graph-with-slider", "figure"),
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

        # Loads dataframe at specific time value by getting the time as a key from a dictionary,
        # then evaluates it to turn it into a python dictionary, and then loads it as a dataframe
        df_by_time = pd.DataFrame.from_dict(literal_eval(json.loads(json_data).get(str(time_value))))

        logging.debug("✅ dataframe filtered by time")

        x_range = list(mdata.get("ranges").get(x_column_name))
        y_range = list(mdata.get("ranges").get(y_column_name))

        logging.debug("✅ X and Y axis ranges created")

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

        logging.debug("✅ Bubble Chart Scatterplot appended for graphing")

        figure = {
            "data": traces_data,
            "layout": dict(
                xaxis={"title": " ".join(x_column_name.split("_")).title(), "range": x_range,},
                yaxis={"title": " ".join(y_column_name.split("_")).title(), "range": y_range,},
                margin={"l": 40, "b": 40, "t": 10, "r": 10},
                legend={"x": 0, "y": 1},
                hovermode="closest",
                # Defines transition behaviors
                transition={"duration": 500, "easing": "cubic-in-out"},
            ),
        }

        logging.debug("✅ Bubble Chart figure created")

        return figure

    @app.callback(
        [Output("play-pause-button", "children"), Output("play-interval", "disabled")],
        [Input("play-pause-button", "n_clicks")],
    )
    def play_pause_switch(n_clicks):
        play_status = str()
        play_bool = bool()
        if n_clicks % 2 == 0:
            play_status, play_bool = ["Pause", False]
        elif n_clicks % 2 != 0:
            play_status, play_bool = ["Play", True]
        return [play_status, play_bool]

    @app.callback(
        Output("time-slider", "value"), [Input("play-interval", "n_intervals")], [State("time-slider", "value")]
    )
    def play_increment(n_intervals, time_value):
        if time_value is None:
            raise PreventUpdate
        print(time_value)
        return str(int(time_value) + 1)

    @app.callback(
        [Output("left-line-plot-graph", "figure"), Output("right-line-plot-graph", "figure")],
        [Input("y_dropdown", "value"), Input("x_dropdown", "value"),],
        [State("df-data", "data"), State("df-mdata", "data")],
    )
    def update_line_plots(left_value, right_value, json_data, mdata):
        """Generates line plots from given data values

        Args:
            y_value (str):y dropdown column name
            x_value (str): x dropdown column name
            json_data (dict): loaded json data from redis
            mdata (dict): extracted metadata from redis
        """
        if None in [left_value, right_value, json_data, mdata]:
            raise PreventUpdate

        x_range = list(mdata.get("ranges").get(right_value))
        y_range = list(mdata.get("ranges").get(left_value))
        # Converts year dict group objects into a dataframe
        framify = lambda frame_dict: pd.DataFrame.from_dict(literal_eval(frame_dict))
        # Generates a dictionary with the keys being time values and the values as tuples of the values for the
        # y dropdown value and x_dropdown value in that order
        time_values = {
            time_val: (framify(data_val)[left_value], framify(data_val)[right_value])
            for time_val, data_val in json.loads(json_data).items()
        }
        left_traces = list()
        right_traces = list()
        left_traces.append(
            Scatter(x=list(time_values.keys()), y=[val[0] for val in list(time_values.values())], mode="lines")
        )
        right_traces.append(
            Scatter(x=list(time_values.keys()), y=[val[1] for val in list(time_values.values())], mode="lines")
        )
        return [
            {
                "data": left_traces,
                "layout": dict(
                    xaxis={"title": " ".join(left_value.split("_")).title(), "autorange": "true"},
                    yaxis={"title": " ".join(left_value.split("_")).title(), "autorange": "true",},
                    margin={"l": 40, "b": 40, "t": 10, "r": 10},
                    legend={"x": 0, "y": 1},
                    hovermode="closest",
                    # Defines transition behaviors
                    transition={"duration": 500, "easing": "cubic-in-out"},
                ),
            },
            {
                "data": right_traces,
                "layout": dict(
                    xaxis={"title": " ".join(right_value.split("_")).title(), "autorange": "true",},
                    yaxis={"title": " ".join(right_value.split("_")).title(), "autorange": "true",},
                    margin={"l": 40, "b": 40, "t": 10, "r": 10},
                    legend={"x": 0, "y": 1},
                    hovermode="closest",
                    # Defines transition behaviors
                    transition={"duration": 500, "easing": "cubic-in-out"},
                ),
            },
        ]

    return app
