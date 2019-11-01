# Import Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import io
import base64

from teslaver.div import MAIN_DIV
from teslaver.layout import LAYOUT


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



def create_app():
    df = load_current_data()

    marks_edited = {str(year): str(year) for year in df['X'].unique()}
    for update_key in list(marks_edited.keys())[::3]:
        # TODO: remove float rendering (maybe start with the casting order?)
        marks_edited[str(int(float(update_key)))] = marks_edited.pop(update_key)

    app = dash.Dash(__name__)

    app.layout = MAIN_DIV
   # html.Div([
   # html.Div([
   #         html.P('Controls', className='card-title labelText', id='controlsTitle'),
   #         ], className='card blue upload-div-exterior')
   # ], id='main_div')
    return app, df


WEB_APP, DATA = create_app()


@WEB_APP.callback(
    # Insures that any update will change the graph, hence all Input and no State
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input('x_dropdown', 'value'),
     Input('y_dropdown', 'value'),
     Input('size_dropdown', 'value'),
     Input('annotation_dropdown', 'value')])
def update_figure(selected_year, x_key, y_key, size_key, annotations_list):
    # Filters to a given x value from the slider
    filtered_DATA = DATA[DATA['X'] == selected_year]
    traces = []
    # Iterates over all 'continents' for a given x value to generate all the bubbles in the graph
    # TODO: Add general handling for other 'contintents' not using the 'name' axis (dropdown/textfield?)
    for i in filtered_DATA.name.unique():
        DATA_by_continent = filtered_DATA[filtered_DATA['name'] == i]
        traces.append(go.Scatter(
            x=DATA_by_continent[x_key],
            y=DATA_by_continent[y_key],
            text=DATA_by_continent[size_key],
            mode='markers',
            opacity=0.7,
            marker={
                # The size is determined from the value of the dropdown given for size,
                # and starts at a default size of 15 with no data and scales
                'size': list(map(lambda increm: int((50 * (increm/100)) + 15),
                                 list(DATA_by_continent[size_key].fillna(0)))),
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    layout = {
        'data': traces,
        # Lays out axis types and ranges based on slider slections
        'layout': dict(
            xaxis={
                'type': 'log',
                'title': ' '.join(x_key.split('_')).title(),
                'range': [
                    min(DATA[x_key]) * 0.9,
                    max(DATA[x_key]) * 1.1,
                ]
            },
            yaxis={
                'title': ' '.join(y_key.split('_')).title(),
                'range': [
                    min(DATA[y_key]) * 0.9,
                    max(DATA[y_key]) * 1.1,
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
    return layout
