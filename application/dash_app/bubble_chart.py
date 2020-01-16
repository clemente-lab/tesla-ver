import dash
import base64
import io

from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import pandas as pd
from .callbacks import create_callbacks
from .layout import LAYOUT



def create_bubble_graph(server):
    app = dash.Dash(server = server,
                    routes_pathname_prefix = '/bubble_graph/')  # , external_stylesheets = external_stylesheets)

    app.layout = LAYOUT
    create_callbacks(app)
    return app.server
