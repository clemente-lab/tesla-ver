import dash_html_components as html
import dash_core_components as dcc
import dash_table
import pandas as pd


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
        multiple=False,
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in children[0].columns],
        data=df.to_dict('records'),
    )
])
