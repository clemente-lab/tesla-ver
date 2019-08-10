import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go

df = pd.read_csv('./data/df.csv')

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='year-slider',
        min=df['X'].min(),
        max=df['X'].max(),
        value=df['X'].min(),
        marks={str(year): str(year) for year in df['X'].unique()}
    ),
    html.Div([
        dcc.Dropdown(
            id = 'x_dropdown',
            options = [{"label": i, "value": i} for i in list(filter(lambda x: '_data' in x,df.columns))],
            value = list(filter(lambda x: '_data' in x,df.columns))[0],
            placeholder = 'X Axis Values'
        ),
        dcc.Dropdown(
            id = 'y_dropdown',
            options = [{"label": i, "value": i} for i in list(filter(lambda x: '_data' in x,df.columns))],
            value =  list(filter(lambda x: '_data' in x,df.columns))[1],
            placeholder = 'Y Axis Values'
        ),
        dcc.Dropdown(
            id = 'size_dropdown',
            options = [{"label": i, "value": i} for i in list(filter(lambda x: '_data' in x,df.columns))],
            value = list(filter(lambda x: '_data' in x,df.columns))[2],
            placeholder = 'Sizing Values'
        )
    ])
])

#region
@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value')],
    [State('x_dropdown', 'value'),
    State('y_dropdown', 'value'),
    State('size_dropdown', 'value')])
def update_figure(selected_year, x_key, y_key, size_key):
    filtered_df = df[df['X'] == selected_year]
    traces = []
    for i in filtered_df.name.unique():
        df_by_continent = filtered_df[filtered_df['name'] == i]
        traces.append(go.Scatter(
            x=df_by_continent[x_key],
            y=df_by_continent[y_key],
            text=df_by_continent[size_key],
            mode='markers',
            opacity=0.7,
            marker={
                'size': list(map(lambda increm: int((50 * (increm/100)) + 15), 
                            list(df_by_continent[size_key].fillna(0)))),
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={
                'type': 'log',
                'title': x_key,
                'range': [
                    min(df[x_key]) * 0.9,
                    max(df[x_key])  * 1.1,
                ]
            },
            yaxis={
                'title': y_key,
                'range': [
                    min(df[y_key]) * 0.9,
                    max(df[y_key])  * 1.1,
                ]
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition={
                'duration': 500,
                'easing': 'cubic-in-out'
            }
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)