import dash

import dash
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from base64 import b64decode
from io import StringIO

from tesla_ver.data_uploading_layout import LAYOUT


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
                content is a string passed from the upload component
            """
            _, content_string = content.split(",")
            decoded = b64decode(content_string)
            fileish = StringIO(decoded.decode("utf-8"))
            return pd.read_csv(fileish, sep="\t")

        def parse_multiple_contents(contents, filenames):
            """Parse a Dash Upload into a DataFrame.

            contents is a string read from the upload component.
            filename and date are just information paramteres
            """
            pass

        df = pd.DataFrame()
        if not any([contents, filename]):
            raise PreventUpdate
        if len(contents) > 1:
            parse_multiple_contents(contents, filename)
        else:
            df = upload_string_to_df(*contents)
            print(df.columns)
            return [
                {"visibility": "visible"},
                df.to_dict("records"),
                [{"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns],
            ]

    return app

