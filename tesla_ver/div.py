import dash_core_components as dcc
import dash_html_components as html

# Loads Current iteration of dataset with function
def load_current_data():
    return pd.read_csv("./data/df.csv")


df = load_current_data()

MAIN_DIV = html.Div(
    [
        Y_AXIS,
        X_AXIS,
        SIZE_AXIS,
        MDATA_TAGS,
        html.P("Controls", className="card-title labelText", id="controlsTitle"),
    ],
    className="card orange lighten-1 z-depth-3",
    id="controls_div",
)

# Div exists as a styling container for graph/slider
GRAPH = html.Div(
    [
        # Provides an empty graph object for updates in callback
        dcc.Graph(id="graph-with-slider"),
        # Creates Slider from min-max X values to give input for graph updates
        dcc.Slider(
            id="year-slider",
            min=df["X"].min(),
            max=df["X"].max(),
            value=df["X"].min(),
            marks=marks_edited,
            updatemode="drag",
        ),
    ],
    className="card z-depth-3",
    id="graph_div",
)

# Used to define metadata tags for the each bubble
MDATA_TAGS = (
    html.Div(
        [
            html.Span("Annotation Metadata:", className="labelText"),
            dcc.Dropdown(
                id="annotation_dropdown",
                options=[{"label": i, "value": i} for i in list(df.columns)],
                value=list(filter(lambda x: "_data" in x, df.columns))[2],
                placeholder="Sizing Values",
                multi=True,
                className="dropdowns",
            ),
        ],
        className="axes_div",
    ),
)

# Used as Label/Input for graph axes
SIZE_AXIS = (
    html.Div(
        [
            html.Span("Size:", className="labelText"),
            dcc.Dropdown(
                id="size_dropdown",
                options=[
                    {"label": i, "value": i}
                    for i in list(filter(lambda x: "_data" in x, df.columns))
                ],
                value=list(filter(lambda x: "_data" in x, df.columns))[2],
                placeholder="Sizing Values",
                className="dropdowns",
            ),
        ],
        className="axes_div",
    ),
)

# Used as Label/Input for graph axes
Y_AXIS = (
    html.Div(
        [
            html.Span("Y:", className="labelText"),
            dcc.Dropdown(
                id="y_dropdown",
                options=[
                    {"label": i, "value": i}
                    for i in list(filter(lambda x: "_data" in x, df.columns))
                ],
                value=list(filter(lambda x: "_data" in x, df.columns))[1],
                placeholder="Y Axis Values",
                className="dropdowns",
            ),
        ],
        className="axes_div",
    ),
)

# Used as Label/Input for graph axes
X_AXIS = html.Div(
    [
        html.Span("X:", className="labelText"),
        dcc.Dropdown(
            id="x_dropdown",
            options=[
                {"label": i, "value": i}
                for i in list(filter(lambda x: "_data" in x, df.columns))
            ],
            value=list(filter(lambda x: "_data" in x, df.columns))[0],
            placeholder="X Axis Values",
            className="dropdowns",
        ),
    ],
    className="axes_div",
)

UPLOAD_DIV = html.Div(
    [
        html.Div(
            [
                html.Span("Upload Loclust Trajectories"),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderStyle": "solid",
                        "borderWidth": "1px",
                        "borderColor": "black",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                    # Allow multiple files to be uploaded
                    multiple=False,
                ),
            ],
            className="card white upload-div-interior",
        )
    ],
    className="card blue upload-div-exterior",
)
