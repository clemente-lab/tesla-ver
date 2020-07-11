import dash
import redis

import pandas as pd
import pyarrow as pa


from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from base64 import b64decode
from io import StringIO

from tesla_ver.data_uploading.data_uploading_layout import LAYOUT
from tesla_ver.redis_manager import redis_manager


def generate_data_uploading(server):
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
        def upload_string_to_df(content):
            """Parse a dash upload string into a single dataframe

                Args:
                    content (b64 string): string passed from the upload component
            """
            _, content_string = content.split(",")
            decoded = b64decode(content_string)
            fileish = StringIO(decoded.decode("utf-8"))
            return pd.read_csv(fileish, sep="\t")

        def parse_multiple_contents(contents, filenames):
            """parses and merges multiple dataframes into a single selection

            Args:
                contents (list(b64 encoded string)): list of base64 encoded strings representing dataframes from dash upload
                filenames (list(str)): list of file names corresponding to each dataframe
            """
            pass

        df = pd.DataFrame()
        if None in [contents, filename]:
            raise PreventUpdate
        if len(contents) > 1:
            parse_multiple_contents(contents, filename)
        else:
            df = upload_string_to_df(*contents)
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
        # Generates a list of dictionaries that style the selected rows and columns with a light blue highlight
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
        if None in [button_clicks, data_dict, selected_columns]:
            raise PreventUpdate

        # if selected_columns is None:
        #     raise DataColumnsNotSelectedError

        df = (
            pd.DataFrame.from_records(data_dict)
            if selected_rows is None
            else pd.DataFrame.from_records(data_dict).iloc[selected_rows]
        )

        if selected_rows is None or len(selected_rows) == 0:
            print(selected_rows)
            selected_rows = list(df.index.values)

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
        redis_manager.redis.set("test", "Hello World, this is a test!")
        return {"visibility": "visible"}

    return app

