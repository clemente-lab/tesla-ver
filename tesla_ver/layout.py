import dash_html_components as html
import dash_core_components as dcc


# The HTML layout for the tesla-ver web app
# All parts of the webpage should be part of the 'children'
# of 'graph_div', the top level div
LAYOUT = html.Div(
    className='card z-depth-3',
    id='graph_div',
    children=[
        # This handles the upload of files
        dcc.Upload(
            id='upload',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            multiple=False,
        ),
        # This triggers the plot to load
        html.Div(id='button',
                 children=[
                    html.Button('Graph', id='upload-button', n_clicks=0)]),

        # This contains all the components of the graph itself
        html.Div(id='graph',
                 # All graph components should go here
                 children=[
                     # Provides an empty graph object for updates in callback
                     dcc.Graph(id='graph-with-slider'),
                     # Creates Slider from min-max X values...
                     # to give input for graph updates

                    html.Div([
                        dcc.Slider(id='year-slider', min=0,
                                   max=1,
                                   value=None,
                                   marks={},
                                   updatemode='drag'
                                   )]),

                    html.Div(id='dropdown_menus',
                             children=[
                                html.Div([
                                    html.P('Y Axis'),
                                    dcc.Dropdown(
                                        id='y_dropdown',
                                        options=[],
                                        value=None,
                                        placeholder='Y Axis Values',
                                        className='dropdowns'
                                        ),
                                        ]),

                                html.Div([
                                    html.P('X Axis'),
                                    dcc.Dropdown(
                                        id='x_dropdown',
                                        options=[],
                                        value=None,
                                        placeholder='X Axis Values',
                                        className='dropdowns'
                                        ),
                                        ]),

                                html.Div([
                                    html.P('Sizing Values'),
                                    dcc.Dropdown(
                                        id='size_dropdown',
                                        options=[],
                                        value=None,
                                        placeholder='Sizing Values',
                                        className='dropdowns'
                                        ),
                                        ]),

                                html.Div([
                                    html.P('Annotation'),
                                    dcc.Dropdown(
                                        id='annotation_dropdown',
                                        options=[],
                                        value=None,
                                        placeholder='Annotation',
                                        multi=True,
                                        className='dropdowns'
                                        )
                                    ]),
                              ])
                          ]),

        # Hidden component for storing data
        html.Div(id='hidden-data', style={'display': 'none'}),
        # End outer div's children
    ],
    # End outer div
)
