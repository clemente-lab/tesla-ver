import datetime
import dash
import base64
import io

import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State

import pandas as pd

# from teslaver.layout import LAYOUT

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

LAYOUT = html.Div([
    dcc.Upload(
        id='upload',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
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
        # Allow multiple files to be uploaded
        multiple=True,
    ),
    html.Div(id='table')
])


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = LAYOUT


marks_edited =  {str(year): str(year) for year in df['X'].unique()}
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    print(type(decoded))
    fileish = io.StringIO(decoded.decode('utf-8'))
    print(fileish)

    df = pd.read_csv(fileish)

    main_div = html.Div([
        html.P('Controls', className='card-title labelText', id='controlsTitle'),
        # Used as Label/Input for graph axes
        html.Div([
            html.Span('X:', className='labelText'),
            dcc.Dropdown(
                id='x_dropdown',
                options=[{"label": i, "value": i} for i in list(filter(lambda x: '_data' in x, df.columns))],
                value=list(filter(lambda x: '_data' in x, df.columns))[0],
                placeholder='X Axis Values',
                className='dropdowns'
            )
        ], className='axes_div'),
        # Used as Label/Input for graph axes
        html.Div([
            html.Span('Y:', className='labelText'),
            dcc.Dropdown(
                id='y_dropdown',
                options=[{"label": i, "value": i} for i in list(filter(lambda x: '_data' in x, df.columns))],
                value=list(filter(lambda x: '_data' in x, df.columns))[1],
                placeholder='Y Axis Values',
                className='dropdowns'
            ),
        ], className='axes_div'),
        # Used as Label/Input for graph axes
        html.Div([
            html.Span('Size:', className='labelText'),
            dcc.Dropdown(
                id='size_dropdown',
                options=[{"label": i, "value": i} for i in list(filter(lambda x: '_data' in x, df.columns))],
                value=list(filter(lambda x: '_data' in x, df.columns))[2],
                placeholder='Sizing Values',
                className='dropdowns'
            )
        ], className='axes_div'),
        # Used to define metadata tags for the each bubble
        html.Div([
            html.Span('Annotation Metadata:', className='labelText'),
            dcc.Dropdown(
                id='annotation_dropdown',
                options=[{"label": i, "value": i} for i in list(df.columns)],
                value=list(filter(lambda x: '_data' in x, df.columns))[2],
                placeholder='Sizing Values',
                multi=True,
                className='dropdowns'
            )
        ], className='axes_div'),
    ], className='card orange lighten-1 z-depth-3', id='controls_div'),
    # Div exists as a styling container for graph/slider
    html.Div([
        # Provides an empty graph object for updates in callback
        dcc.Graph(id='graph-with-slider'),
        # Creates Slider from min-max X values to give input for graph updates
        dcc.Slider(
            id='year-slider',
            min=df['X'].min(),
            max=df['X'].max(),
            value=df['X'].min(),
            marks=marks_edited,
            updatemode='drag'
        ),
    ],  className='card z-depth-3', id='graph_div'),
    html.Div([
        html.Div([
            html.Span('Upload Loclust Trajectories'),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderStyle': 'solid',
                    'borderWidth': '1px',
                    'borderColor': 'black',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            )
        ], className='card white upload-div-interior')
    ], className='card blue upload-div-exterior')

    return main_div


@app.callback(Output('table', 'children'),
              [Input('upload', 'contents')],
              [State('upload', 'filename'),
               State('upload', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)
