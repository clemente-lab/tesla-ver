import dash
import json

import pandas as pd
import pyarrow as pa

from flask import session

from ast import literal_eval
from plotly.graph_objects import Scatter
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from tesla_ver.charting.charting_layout import LAYOUT
from tesla_ver.redis_manager import redis_manager


def generate_charting(server):

    # TODO Use metadata in charting/graphing system, reenable feature flag when metadata is used for charting/graphing

    app = dash.Dash(__name__, server=server, url_base_pathname="/bubblechart.html/")

    app.layout = LAYOUT

    # Ignores callback exceptions -- this is to allow for the initial state of the time value to be set
    # without raising errors
    app.config.suppress_callback_exceptions = True

    server.logger.debug("Bubble Chart layout loaded")

    @app.callback(
        [
            Output("df-timedata", "data"),
            Output("df-iddata", "data"),
            Output("df-mdata", "data"),
            Output("graph", "style"),
            Output("button", "style"),
        ],
        [Input("upload-button", "n_clicks"),],
    )
    def load_redis_data(n_clicks):
        if n_clicks == 0:
            server.logger.debug("Bubble Chart Load Data Initial State Set")
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

        # Gets session UUID to get user specific data
        session_uuid = session.get('uuid')

        if redis_manager.redis.exists(session_uuid + "_numeric_data"):

            # User specific key for data stored in redis
            numeric_data_key = session_uuid + "_numeric_data"

            server.logger.debug("reading data from redis key: " + numeric_data_key)

            df = context.deserialize(redis_manager.redis.get(session_uuid + "_numeric_data"))

            # Clear user specific data after read
            redis_manager.redis.delete(numeric_data_key)
        else:
            # Because of the need to return data matching all the different areas, displaying an error message
            # to the end user would require either another callback to chain with, which would complicate the code and
            # likely add a small bit of latency, which is this is left as a console-based error message.
            raise PreventUpdate("Data could not be loaded from redis")

        server.logger.debug("redis data for UUID " + session_uuid + " flushed")

        mdata = extract_mdata(df, "Year")
        df.rename(columns={"Year": "X"}, inplace=True)

        server.logger.debug("numeric dataframe processed from redis")

        # This lambda takes a tidy dataframe, and turns it into a dict where they keys are the group values
        # and the values are the grouped dataframe chunks.
        # This is used to remove the need to compute a groupby on every callback, which would be a major performance hit.
        grouper = lambda df, col: json.dumps(
            {group_name: df_group.to_json() for group_name, df_group in df.groupby(col)}
        )
        return [grouper(df, "X"), grouper(df, "Subject"), mdata, {"visibility": "visible"}, {"visibility": "hidden"}]

    @app.callback(
        [
            Output("time-slider", "marks"),
            Output("time-slider", "min"),
            Output("time-slider", "max"),
            Output("time-slider", "value"),
        ],
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
        server.logger.debug(f"✅ Marks Dictionary Created, time values are: {marks.keys()}")
        return [marks, time_min, time_max, time_min]

    @app.callback(
        [
            Output("y_dropdown", "options"),
            Output("x_dropdown", "options"),
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

        server.logger.debug(f'✅ Data Options created, values are {mdata.get("data_cols")}')

        return [
            data_options,
            data_options,
        ]

    @app.callback(
        Output("bubble-graph-with-slider", "figure"),
        [Input("time-slider", "value"), Input("y_dropdown", "value"), Input("x_dropdown", "value"),],
        [State("df-timedata", "data"), State("time-slider", "marks"), State("df-mdata", "data")],
    )
    def update_figure(time_value, y_column_name, x_column_name, json_data, marks, mdata):
        """This callback handles updating the graph in response to user
        actions."""
        # Prevents updates without data
        if None in [json_data, x_column_name, y_column_name, mdata]:
            raise PreventUpdate(
                "Graph could not load data -- either this is at startup, or the Storage component isn't storing the data"
            )

        if time_value == None:
            time_value = int(mdata.get("time_min"))

        # Loads dataframe at specific time value by getting the time as a key from a dictionary,
        # then evaluates it to turn it into a python dictionary, and then loads it as a dataframe
        try:
            df_by_time = pd.DataFrame.from_dict(literal_eval(json.loads(json_data).get(str(time_value))))
        except ValueError:
            pass

        server.logger.debug("✅ dataframe filtered by time")

        x_range = list(mdata.get("ranges").get(x_column_name))
        y_range = list(mdata.get("ranges").get(y_column_name))

        server.logger.debug("✅ X and Y axis ranges created")

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

        server.logger.debug("✅ Bubble Chart Scatterplot appended for graphing")

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

        server.logger.debug("✅ Bubble Chart figure created")

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
        return str(int(time_value) + 1)

    @app.callback(
        [Output("left-line-plot-graph", "figure"), Output("right-line-plot-graph", "figure")],
        [Input("y_dropdown", "value"), Input("x_dropdown", "value"),],
        [State("df-iddata", "data"), State("df-mdata", "data")],
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

        # Generates ranges for x and y dropdowns dependent values
        x_range = list(mdata.get("ranges").get(right_value))
        y_range = list(mdata.get("ranges").get(left_value))

        # Left and right scatterplot lists
        left_traces, right_traces = list(), list()

        # Populates lists of scatterplots by iterating over id
        for subject in literal_eval(json_data).keys():
            df = pd.DataFrame.from_dict(literal_eval(json.loads(json_data).get(str(subject))))
            left_traces.append(Scatter(x=df["X"], y=df[left_value], mode="lines", name=f"Subject: {subject}"))
            right_traces.append(Scatter(x=df["X"], y=df[right_value], mode="lines", name=f"Subject: {subject}"))
        # Generates title from column names
        dependentTitle = lambda value: " ".join(value.split("_")).title()
        return [
            {
                "data": left_traces,
                "layout": dict(
                    xaxis={"title": "Time", "autorange": "true"},
                    yaxis={"title": dependentTitle(left_value), "autorange": "true",},
                    title={
                        "text": f"{dependentTitle(left_value)} vs Time",
                        "y": 0.9,
                        "x": 0.5,
                        "xanchor": "center",
                        "yanchor": "top",
                    },
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
                    xaxis={"title": "Time", "autorange": "true",},
                    yaxis={"title": dependentTitle(right_value), "autorange": "true",},
                    title={
                        "text": f"{dependentTitle(right_value)} vs Time",
                        "y": 0.9,
                        "x": 0.5,
                        "xanchor": "center",
                        "yanchor": "top",
                    },
                    margin={"l": 40, "b": 40, "t": 10, "r": 10},
                    legend={"x": 0, "y": 1},
                    hovermode="closest",
                    # Defines transition behaviors
                    transition={"duration": 500, "easing": "cubic-in-out"},
                ),
            },
        ]

    return app
