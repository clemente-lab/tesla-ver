# -*- coding: utf-8 -*-
"""
Created On Friday July 11

@author: alexanderkyim
"""

#region
#import dash and components
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

#import graphing library(ies)
import plotly
import plotly.graph_objs as go

#import data manipulation libraries
import numpy as np
import pandas as pd
import base64
import io
import loclust
import scripts.loclust_traj_to_json
from scripts.JSONWrapper import JSONWrapper
from scripts.json_helpers import parse_loclust_string_to_json, get_X_and_Y, get_keys_metadata
import csv
import httplib
import json
#misc imports
import os
#endregion

app = dash.Dash(__name__, external_stylesheets=['https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css'], 
                                external_scripts=[' https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'])
app.config['suppress_callback_exceptions']=True

# server = app.server
# app.config.supress_callback_exceptions = False
XandY = get_X_and_Y()
app.layout = html.Div([
    html.Div([
        html.H1('Teslaver')
    ], style={
        'text-align':'center',
    }),
    html.Div([
        dcc.Dropdown(id="selected-type", options=[{"label": i, "value": i} for i in get_keys_metadata()]),
    ], style={
    }),
    
    dcc.Graph(
        id='heatmap-main',
        # hoverData = 'points':[{'0':}]
    ),
    html.P([dcc.Slider(
        id='main-slider',
        min=min(XandY.get('X')),
        max=max(XandY.get('X')),
        value=min(XandY.get('X')),
        marks={str(X): str(X) for X in XandY.get('X')},
    ),
    ],
    style = {
            'margin-top':'5px',
            'width' : '80%',
            'fontSize' : '20px',
            'padding-left' : '100px',
            'display': 'inline-block'}),
    html.Label('Time Interval', style={'text-align':'center',
        'margin':'auto',
        'padding-top':'20px',
        'display':'block',}),
    html.P([
        html.Button('Draw Graphs', id='draw-button', className='waves-effect waves-light btn-large'),
        html.Button('Reload Graphs', id='reload-button', className='waves-effect waves-light btn-large'),
    ],
    style = {
        'margin-top':'5px',
        'padding-top':'10px',
        'display':'inline-block',
    }
    ),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ', html.A('Select Files', className='card-content white-text')
        ], className='card-content white-text'),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'text-align': 'center',
            # 'display': 'flex',
            # 'margin': '10px',
        },
        className = 'card blue',
        # Disallow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    html.Div(id='graph-div'),
    html.Div(id='hidden-div'),

])
# style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'})


# @app.callback(Output('hidden-div', 'children'),
#             [Input('shutdown-button', 'n_clicks')])
# def call_shutdown(contents):
#     shutdown_call = Process(target=shutdown_server)
#     shutdown_call.start()
#     shutdown_call.join()


@app.callback(Output('graph-div', 'children'),
              [Input('main-slider', 'value')])
def draw_heat_map(n_clicks):
    pass



@app.callback([Output('output-data-upload', 'children'),
                            Output('selected-type', 'options')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(file_to_upload, file_name):
    if file_to_upload is not None:
        if os.path.exists('./assets/json_data/db.json'):
            os.remove('./assets/json_data/db.json')
        return parse_contents(file_to_upload,file_name), [{"label": i, "value": i} for i in get_keys_metadata()]

def parse_contents(contents, filename):
    # print contents
    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            #User uploaded loclust csv
            parse_loclust_string_to_json(io.StringIO(decoded.decode('utf-8')).getvalue(), filename)
            return html.Div([
                u'✅ Data successfully loaded and appears ready',
            ])
    except Exception as e:
        print(e)
        return html.Div([
            u'❌ There was an error processing this file, or you uploaded a non-loclust file'
        ])

#region
# from flask import request
# def shutdown_server():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()

# @app.server.route('/shutdown', methods=['POST'])
# def shutdown():
#     shutdown_server()
#     return 'Server shutting down...'
#endregion

if __name__ == '__main__':
    app.run_server(debug=True)
