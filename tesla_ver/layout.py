import dash_html_components as html
import dash_core_components as dcc


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
