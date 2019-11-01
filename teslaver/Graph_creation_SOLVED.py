
import base64
import io
import os

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import json


from flask import send_from_directory
import pandas as pd

# # App and divs:
app = dash.Dash(__name__)

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = html.Div(
    children=[
        html.Link(rel='stylesheet', href='/static/dash.css'),


        html.Div(
            className='row', children=[html.H1('Dynamic Plot Creation', style={'text-align':'left', 'padding-left': '10px'})]),


        html.Div(className='row', children=[
            html.Div(className='colLeft', children=[
                html.Div(className='colContainer', children=[
                    html.H2('Data Processing Section:'),

                    html.H3('Step 1: Load data:', className='steps'),
                    dcc.Upload(className='button_upload', id='upload-data', multiple=True, children=html.Div(id='upload_text_box', children=['Drag and Drop or ',
                                                                                                                                             html.A('Click to Select Files'),
                                                                                                                                             ],
                                                                                                             ),
                               ),

                    html.Div(className='column_selector', children=[html.H3('Step 2. Select a column to visualise distribution:'),

                                                                    dcc.Dropdown(value=['Please load data.'],
                                                                                 options=[{'label': i, 'value': i} for i in ['Please load data.']],
                                                                                 multi=False,
                                                                                 id='target_col_dropdown',
                                                                                 className='dropdownSelect'
                                                                                 ),
                                                                    html.P(id='target_col'),
                                                                    ]
                             ),




                ]
                )


            ]
            ),

            html.Div(className='colRight', children=[
                html.Div(className='colContainer', children=[html.H2("Visualisation Section"),
                                                             html.Div(children=[html.H4('Please load a data file in order to populate a table and visualisation below', id='output-data-upload')]),
                                                             html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
                                                             html.Div(id='target_col_distribution_div', children=[dcc.Graph(id='target_col_dist')])
                                                             ]
                         )

            ]
            ),

        ]
        ),

                                # hidden variables stored in the web browser:
                                html.Div(id='intermediate-value', style={'display': 'none'}),
                                html.Div(id='target_col_selection', style={'display': 'none'}),

                                ])

###### CALL BACKS: ######
def parse_pandas_data(contents, filename, date):

    '''Desc: Parse the contents of uploaded file'''

    content_type, content_string=contents.split(',')
    decoded = base64.b64decode(content_string)
    possible_encodings = ['latin-1', 'utf-8']

    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            for i in possible_encodings: # try different encodings
                try:
                    df = pd.read_csv(io.StringIO(decoded.decode(i)))
                    global df_cols
                    df_cols = list(df.columns)
                    break

                except Exception as ude:
                    print("Encoding is not %s" %(i))

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df

# Loading the CSS file:
@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)

# load pandas data file and store in a Div:
@app.callback(Output('intermediate-value', 'children'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename'),
               Input('upload-data', 'last_modified')])
def load_data(list_of_contents, list_of_names, list_of_dates):

        data = [parse_pandas_data(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)][0]

        return data.to_json()



# updating the target dropdown menu with columns from loaded data:
@app.callback(Output('target_col_dropdown', 'options'),
              [Input('intermediate-value', 'children')])
def set_target_col_options(jsonified_data):

    dff = pd.read_json(jsonified_data) # or, more generally json.loads(jsonified_cleaned_data)

    return [{'label': i, 'value': i} for i in list(dff.columns)]


# Storing the target col:
@app.callback(Output('target_col_selection', 'children'),
              [Input('target_col_dropdown', 'value')])
def save_target_output(value):
    n = json.dumps({'target': value})
    return n

# Drawing the distribution of the target column
@app.callback(Output('target_col_dist', 'figure'),
              [Input('target_col_dropdown', 'value'),
               Input('intermediate-value', 'children')])
def draw_target_col_dist(column, jsonified_data):

    dff = pd.read_json(jsonified_data)
    counts = dff[column].value_counts()
    keys = counts.index.tolist()
    values = counts.values.tolist()

    data = [go.Bar(
        x=keys,
        y=values,
    )
    ]

    bar_figure = {'data': data}

    return bar_figure


# updating the table with loaded data:
@app.callback(Output('output-data-upload', 'children'),
              [Input('intermediate-value', 'children')])
def update_table_output(jsonified_data):

    dff = pd.read_json(jsonified_data)

    return html.Div([
        html.H3("View loaded data below:", style={'margin-left':'0'}),
        dt.DataTable(rows=dff.to_dict('records')),

        html.Hr(),
        html.Br(),
        html.H3("Please select columns in the left pane to produce a visualisation below")
    ])



if __name__ == '__main__':
    app.run_server(debug=True)
