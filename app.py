import datetime
import dash
import base64
import io

import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import pandas as pd

# from teslaver.layout import LAYOUT

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


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
            'borderRadius': '50px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True,
    ),
    html.Div(id='graph'),
    html.Div([
        # Provides an empty graph object for updates in callback
        dcc.Graph(id='graph-with-slider'),
        # Creates Slider from min-max X values to give input for graph updates
        dcc.Slider(
            id='year-slider',
            min=0,  # df['X'].min(),
            max=1,  # df['X'].max(),
            value=0,  # df['X'].min(),
            marks={'0': '0', '1': '1'},  # marks_edited,
            updatemode='drag'
        ),
    ],
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '50px',
            'textAlign': 'center',
            'margin': '10px'
        },
        className='card z-depth-3', id='graph_div'),
    # Hidden component for storing data
    html.Div(id='hidden-data', style={'display': 'none'}),
])


app = dash.Dash(__name__)  # , external_stylesheets=external_stylesheets)

app.layout = LAYOUT


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    print(type(decoded))
    fileish = io.StringIO(decoded.decode('utf-8'))
    print(fileish)

    df = pd.read_csv(fileish)
    print(df.columns)

    return df


def build_div(df):
    marks_edited = {str(year): str(year) for year in df['X'].unique()}
    main_div = html.Div([
        html.Div([
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
    ], className='card blue upload-div-exterior')

    return main_div


@app.callback([Output('graph', 'children'),
               Output('hidden-data', 'children'),
               Output('graph-with-slider', 'figure')],
              [Input('upload', 'contents')],
              [State('upload', 'filename'),
               State('upload', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    children = []
    rdf = None
    figure = {}
    if list_of_contents is not None:
        for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
            df = parse_contents(c, n, d)
            children.append(build_div(df))
            rdf = df.to_json()
        x_key = 'ad_fert_data'
        y_key = 'adjusted_income_data'
        size_key = 'contraceptive_data'
        traces = []

        for i in df.name.unique():
            df_by_continent = df[df['name'] == i]
            traces.append(go.Scatter(
                x=df_by_continent[x_key],
                y=df_by_continent[y_key],
                text=df_by_continent[size_key],
                mode='markers',
                opacity=0.7,
                marker={
                    # The size is determined from the value of the dropdown given for size,
                    # and starts at a default size of 15 with no data and scales
                    'size': list(map(lambda increm: int((50 * (increm/100)) + 15),
                                     list(df_by_continent[size_key].fillna(0)))),
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=i
            ))
        figure.update({
            'data': traces,
            # Lays out axis types and ranges based on slider slections
            'layout': dict(
                xaxis={
                    'type': 'log',
                    'title': ' '.join(x_key.split('_')).title(),
                    'range': [
                        min(df[x_key]) * 0.9,
                        max(df[x_key]) * 1.1,
                    ]
                },
                yaxis={
                    'title': ' '.join(y_key.split('_')).title(),
                    'range': [
                        min(df[y_key]) * 0.9,
                        max(df[y_key]) * 1.1,
                    ]
                },
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                # Defines transition behaviors
                transition={
                    'duration': 500,
                    'easing': 'cubic-in-out'
                }
            )
        })
    return children, [rdf], figure

    """
@app.callback(
    # Insures that any update will change the graph, hence all Input and no State
    Output('graph', 'children'),
    Input('hidden-data', 'value'),
    Input('year-slider', 'value'))
    # Input('x_dropdown', 'value'),
    # Input('y_dropdown', 'value'),
    # Input('size_dropdown', 'value'),
    # Input('annotation_dropdown', 'value')])
def update_figure(jdf, selected_year, jdf, x_key, y_key, size_key, annotations_list):
    df = pd.read_json(jdf)
    # Filters to a given x value from the slider
    filtered_df = df[df['X'] == selected_year]
    return [build_div(filtered_df)]
    traces = []
    # Iterates over all 'continents' for a given x value to generate all the bubbles in the graph
    # TODO: Add general handling for other 'contintents' not using the 'name' axis (dropdown/textfield?)
    for i in filtered_df.name.unique():
        df_by_continent = filtered_df[filtered_df['name'] == i]
        traces.append(go.Scatter(
            x=df_by_continent[x_key],
            y=df_by_continent[y_key],
            text=df_by_continent[size_key],
            mode='markers',
            opacity=0.7,
            marker={
                # The size is determined from the value of the dropdown given for size,
                # and starts at a default size of 15 with no data and scales
                'size': list(map(lambda increm: int((50 * (increm/100)) + 15),
                                 list(df_by_continent[size_key].fillna(0)))),
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        # Lays out axis types and ranges based on slider slections
        'layout': dict(
            xaxis={
                'type': 'log',
                'title': ' '.join(x_key.split('_')).title(),
                'range': [
                    min(df[x_key]) * 0.9,
                    max(df[x_key]) * 1.1,
                ]
            },
            yaxis={
                'title': ' '.join(y_key.split('_')).title(),
                'range': [
                    min(df[y_key]) * 0.9,
                    max(df[y_key]) * 1.1,
                ]
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            # Defines transition behaviors
            transition={
                'duration': 500,
                'easing': 'cubic-in-out'
            }
        )
    }
    """


if __name__ == '__main__':
    app.run_server(debug=True)
