import dash_html_components as html
import dash_core_components as dcc
from dash_table import DataTable
import pandas as pd

LAYOUT = html.Div(
    className="card z-depth-3",
    id="graph_div",
    children=[
        # This handles the upload of files
        dcc.Upload(id="upload", children=html.Div(["Drag and Drop or ", html.A("Select Files")]), multiple=True),
        html.Div(
            id="data-table-div",
            children=[
                html.P("Select data columns and rows to graph"),
                # Datatable that gets populated
                DataTable(
                    id="data-table-visualization",
                    columns=[
                        {"name": i, "id": i, "deletable": True, "selectable": True}
                        for i in pd.read_csv(
                            "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
                        ).columns
                    ],
                    data=pd.read_csv(
                        "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
                    ).to_dict("records"),
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="multi",
                    row_selectable="multi",
                    row_deletable=True,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                ),
                html.Button("Upload to redis", id="redis-upload-button", className="card-panel teal"),
            ],
            style={"visibility": "hidden"},
        ),
    ],
)

