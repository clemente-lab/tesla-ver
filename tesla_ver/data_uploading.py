import dash

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from tesla_ver.data_uploading_layout import LAYOUT


def generate_data_uploading(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/datauploading.html/")
    app.layout = LAYOUT
    return app

