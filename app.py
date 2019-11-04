import dash
import base64
import io

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import pandas as pd

# from teslaver.layout import LAYOUT

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


LAYOUT = html.Div(
    [
        dcc.Upload(
            id='upload',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            multiple=False,
        ),
        html.Button(id='upload-button', n_clicks=0, children='Submit'),
        html.Div(id='graph',
                 children=[
                     # Provides an empty graph object for updates in callback
                     dcc.Graph(id='graph-with-slider'),
                     # Creates Slider from min-max X values to give input for graph updates
                     dcc.Slider(
                         id='year-slider',
                         min=0,
                         max=1,
                         value=None,
                         marks={},
                         updatemode='drag'
                     ),
                 ]),
        # Hidden component for storing data
        html.Div(id='hidden-data', style={'display': 'none'})
    ],
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
    className='card z-depth-3', id='graph_div')

app = dash.Dash(__name__)  # , external_stylesheets=external_stylesheets)

app.layout = LAYOUT


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    fileish = io.StringIO(decoded.decode('utf-8'))
    df = pd.read_csv(fileish)

    return df


@app.callback(Output('hidden-data', 'children'),
              [
                  Input('upload', 'contents'),
                  Input('upload', 'filename'),
                  Input('upload', 'last_modified')
              ])
def upload_data(contents, filename, last_modified):
    df = None
    if contents is not None:
        df = parse_contents(contents, filename, last_modified).to_json()
    return df


@app.callback(
    [
        Output('graph', 'style'),
        Output('graph-with-slider', 'figure'),
        Output('year-slider', 'marks'),
        Output('year-slider', 'min'),
        Output('year-slider', 'max')
    ],
    [
        Input('upload-button', 'n_clicks'),
        Input('year-slider', 'value')
    ],
    [
        State('hidden-data', 'children')
    ]
)
def update_figure(clicks, selected_year, df):
    year_min = 0
    year_max = 1
    figure = {}
    marks = {}
    style = {'display': 'none'}
    traces = []
    x_key = 'ad_fert_data'
    y_key = 'adjusted_income_data'
    size_key = 'contraceptive_data'
    if df is not None:
        df = pd.read_json(df)
        marks = {str(year): str(year) for year in df['X'].unique()}
        year_min = df['X'].min()
        year_max = df['X'].max()
        print(marks)
        if selected_year is None:
            filtered_df = df
        else:
            # Filters to a given x value from the slider
            filtered_df = df[df['X'] == selected_year]
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
        style = {
            'width': '100%'
        }
        figure = {
            'data': traces,
            # Lays out axis types and ranges based on slider slections
            'layout': dict(
                xaxis={
                    'type': 'log',
                    'title': ' '.join(x_key.split('_')).title(),
                    'autorange': 'true'
                },
                yaxis={
                    'title': ' '.join(y_key.split('_')).title(),
                    'autorange': 'true'
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
    return style, figure, marks, year_min, year_max


if __name__ == '__main__':
    app.run_server(debug=True)
