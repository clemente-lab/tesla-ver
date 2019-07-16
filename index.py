import os
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
# from apps import main, heatmap

#Set App name for main view
app_name = 'Tesla-ver'


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Tesla-ver</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry}
        <footer>
        </footer>
    </body>
</html>
'''
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# @app.callback(Output('page-content', 'children'),
#               [Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname is None or pathname.replace(app_name, '').strip('/') == '':
#         return main.layout
#     else:
#         return code.layout

if __name__ == '__main__':
    app.run_server(debug=True)