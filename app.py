# -*- coding: utf-8 -*-
"""
Created On Friday July 1

@author: alexanderkyim
"""


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
import csv
import httplib
import json
#misc imports
import os


app = dash.Dash(__name__)

# server = app.server
# app.config.supress_callback_exceptions = False
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ', html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Disallow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    html.Div(id='hidden-div')
])

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
                #TODO: Add callback for button
                html.Button('Draw Graphs', id='draw-button'),
            ])
    except Exception as e:
        print(e)
        return html.Div([
            u'❌ There was an error processing this file, or you uploaded a non-loclust file'
        ])


@app.callback(
    dash.dependencies.Output('hidden-div', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')])
def draw_graphs(n_clicks):
    return str(n_clicks)


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(file_to_upload, file_name):
    if file_to_upload is not None:
        return parse_contents(file_to_upload,file_name)

def parse_loclust_string_to_json(loclust_string, file_name):
    jsonDict = dict()

    #Turns string of input into a 2d list
    split_data = map(lambda x: x.split('\t'), loclust_string.split('\n'))

    #adds a dictionary of all of the keys
    jsonDict['keys'] = split_data[0]

    #Reduces the 2d list to just a list of non keys and removes an empty list at the end
    split_data = split_data[1:-1]

    #Creates a list of tuples of the type (ID, dictionary) where the dictionary is key:value for each ID's list
    #of values, and with the special key 'XYData' to store each X:Y pair in a sub-dictionary
    split_data = [id_list_to_dict(split_data_indiv,jsonDict['keys']) for split_data_indiv in split_data]

    #adds the ID:dictionary pairs from each tuple
    for id_chunk in split_data:
        id_val, dict_val = id_chunk
        jsonDict[id_val] = dict_val
    with open("./assets/json_data/{}.json".format(file_name), "w") as write_file:
        json.dump(jsonDict, write_file)
    # return jsonDict
    
def id_list_to_dict(id_list, keys_list):
    id_dict = dict()

    #Populates X:Y pairs of sub dictionary
    id_dict['XYData'] = {str(key):str(value) for key, value in zip(id_list[1].split(','), id_list[2].split(','))}
    #Creates dictionary of all key:idvalue pairs, now including the XYData
    id_dict.update({str(key):str(value) for key, value in zip(keys_list[3:], id_list[3:])})
    #Returns a tuple with the original ID and the new dictionary corresponding to that ID
    return (id_list[0],id_dict)

if __name__ == '__main__':
    app.run_server(debug=True)