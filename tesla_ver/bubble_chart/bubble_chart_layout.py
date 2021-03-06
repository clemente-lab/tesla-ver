import dash_html_components as html
import dash_core_components as dcc


# The HTML layout for the tesla-ver web app
# All parts of the webpage should be part of the 'children'
# of 'graph_div', the top level div
LAYOUT = html.Div(
    className="card z-depth-3",
    id="graph_div",
    children=[
        # This triggers the plot to load
        html.Div(id="button", children=[html.Button("Graph", id="upload-button", n_clicks=0)]),
        # This contains all the components of the graph itself
        html.Div(
            id="graph",
            # All graph components should go here
            children=[
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="Bubble Chart Animation",
                            children=[  # Provides an empty graph object for updates in callback
                                dcc.Graph(id="bubble-graph-with-slider"),
                                # Div contains play/pause button and slider
                                # Creates Slider from min-max X values
                                # to give input for graph updates
                                html.Div(
                                    id="controls-div",
                                    children=[
                                        html.Button("Play", id="play-pause-button", n_clicks=1),
                                        dcc.Interval(
                                            id="play-interval", interval=1 * 1000, n_intervals=0, disabled=True
                                        ),
                                        dcc.Slider(
                                            id="time-slider", min=0, max=1, value=None, marks={}, updatemode="drag",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dcc.Tab(
                            label="Line Plots",
                            children=[
                                html.Div(
                                    children=[dcc.Graph(id="left-line-plot-graph")],
                                    style={"width": "45%", "display": "inline-block"},
                                ),
                                html.Div(
                                    children=[dcc.Graph(id="right-line-plot-graph")],
                                    style={"width": "45%", "display": "inline-block"},
                                ),
                            ],
                        ),
                    ]
                ),
                html.Div(
                    id="dropdown_menus",
                    children=[
                        html.Div(
                            [
                                html.P("Y Axis"),
                                dcc.Dropdown(
                                    id="y_dropdown",
                                    options=[],
                                    value=None,
                                    placeholder="Y Axis Values",
                                    className="dropdowns",
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.P("X Axis"),
                                dcc.Dropdown(
                                    id="x_dropdown",
                                    options=[],
                                    value=None,
                                    placeholder="X Axis Values",
                                    className="dropdowns",
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.P("Sizing Values"),
                                dcc.Dropdown(
                                    id="size_dropdown",
                                    options=[],
                                    value=None,
                                    placeholder="Sizing Values",
                                    className="dropdowns",
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.P("Annotation"),
                                dcc.Dropdown(
                                    id="annotation_dropdown",
                                    options=[],
                                    value=None,
                                    placeholder="Annotation",
                                    multi=True,
                                    className="dropdowns",
                                ),
                            ]
                        ),
                    ],
                ),
            ],
            style={"visibility": "visible"},
        ),
        # Storage component for storing parsed data
        dcc.Store(id="df-timedata"),
        # Stores metadata from parsed data  with the "int" being a standin for whatever time format is used
        # (in the format {time_max:int, time_min:int, x_vals:list(int), numeric_cols:list(str), mdata_cols:list(str)})
        dcc.Store(id="df-mdata"),
        # Stores grouped id data
        dcc.Store(id="df-iddata"),
        # End outer div's children
    ],
    # End outer div
)
