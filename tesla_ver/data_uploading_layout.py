import dash_html_components as html
import dash_core_components as dcc
from dash_table import DataTable

LAYOUT = html.Div(
    className="card z-depth-3",
    id="graph_div",
    children=[
        # This handles the upload of files
        dcc.Upload(id="upload", children=html.Div(["Drag and Drop or ", html.A("Select Files")]), multiple=True),
        html.P("Select data columns and rows to graph"),
        # Datatable that gets populated
        DataTable(
            id="data-table-visualization",
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
        html.Button("Upload to redis", id="redis-upload", className="card-panel teal"),
    ],
)

