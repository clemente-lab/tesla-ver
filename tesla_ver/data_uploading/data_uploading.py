import dash
import redis

import pandas as pd
import numpy as np
import pyarrow as pa


from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from tesla_ver.data_uploading.data_uploading_layout import LAYOUT
from tesla_ver.redis_manager import redis_manager
from tesla_ver.data_uploading.utils import upload_string_to_df


def generate_data_uploading(server):
    """Generates a dash app and attaches it to an existing flask server

    Args:
        server (Flask): Flask app to attach data uploading screen to

    Raises:
        PreventUpdate: Prevents using none values, since dash has to set initial state
        PreventUpdate: Also prevents using none values since dash has to set initial state

    Returns:
        Dash: dash app with data uploading screen
    """
    app = dash.Dash(__name__, server=server, url_base_pathname="/datauploading.html/")
    app.layout = LAYOUT

    @app.callback(
        [
            Output("data-table-div", "style"),
            Output("data-table-visualization", "data"),
            Output("data-table-visualization", "columns"),
        ],
        [Input("upload", "contents"), Input("upload", "filename")],
    )
    def upload_data_parsing(contents, filename):
        """Parses csv file uploaded into a dataframe

        Args:
            contents (Base64(str)): Base64 encoded string of dataframe values from csv
            filename (str): name of file
        """

        df = pd.DataFrame()
        if None in [contents, filename]:
            raise PreventUpdate
        else:
            df = upload_string_to_df(contents)

            # Removes Nan, negativve, and infinite values from the dataframe and replaces sets them to 0
            df[df < 0] = 0
            df[~df.isin([np.nan, np.inf, -np.inf]).any(axis=1)]
            df = df.fillna(0)
            return [
                {"visibility": "visible"},
                df.to_dict("records"),
                [{"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns],
            ]

    @app.callback(
        Output("data-table-visualization", "style_data_conditional"),
        [Input("data-table-visualization", "selected_columns"), Input("data-table-visualization", "selected_rows"),],
    )
    def update_styles(selected_columns, selected_rows):
        """Generates a list of dictionaries that style the selected rows and columns with a light blue highlight

        Args:
            selected_columns (list): list of selected columns
            selected_rows (list): list of selected rows

        Returns:
            dict: dictionary of styling values with highlighted styling for selected columns and rows
        """
        return [
            *[{"if": {"column_id": i}, "background_color": "#D2F3FF"} for i in selected_columns],
            *[{"if": {"row_index": i}, "background_color": "#D2F3FF"} for i in selected_rows],
        ]

    @app.callback(
        Output("upload-confirmation", "style"),
        [Input("redis-upload-button", "n_clicks")],
        [
            State("data-table-visualization", "data"),
            State("data-table-visualization", "selected_columns"),
            State("data-table-visualization", "selected_rows"),
        ],
    )
    def push_to_redis(button_clicks, data_dict, selected_columns, selected_rows):
        """Pushes dataframe and selection subset to redis cache

        Args:
            button_clicks (int): number of clicks of the button -- exists to start update
            data_dict (dict): dictionary of all uploaded data -- pulled from the datatable
            selected_columns (list): list of selected column names
            selected_rows (list of selected): list of selected row indicies

        Raises:
            PreventUpdate: prevents initial setstate from causing errors

        Returns:
            dict: sets a confirmation message to be visible
        """
        if None in [button_clicks, data_dict, selected_columns]:
            raise PreventUpdate

        df = (
            pd.DataFrame.from_records(data_dict)
            if not selected_rows
            else pd.DataFrame.from_records(data_dict).iloc[selected_rows]
        )

        mdata_cols = sorted(set(df.columns) - set(selected_columns))

        serialization_context = pa.default_serialization_context()

        redis_manager.redis.set(
            "data_numeric",
            serialization_context.serialize(df[sorted(set(["Year", "Subject", *selected_columns]))])
            .to_buffer()
            .to_pybytes(),
        )
        redis_manager.redis.set(
            "data_mdata",
            serialization_context.serialize(df[["Year", "Subject", *mdata_cols]]).to_buffer().to_pybytes(),
        )
        return {"visibility": "visible"}

    return app

