import dash
import base64
import io

from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import pandas as pd

def create_callbacks(app):
  def parse_contents(contents, filename, date):
        """ Parse a Dash Upload into a DataFrame """
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        fileish = io.StringIO(decoded.decode('utf-8'))
        df = pd.read_csv(fileish)
        return df


  @app.callback(Output('hidden-data', 'children'),
              [
                  Input('upload', 'contents'),
                  Input('upload', 'filename'),
                  Input('upload', 'last_modified')
              ])
  def upload_data(contents, filename, last_modified):
    """ This callback handles storing the dataframe as JSON in the hidden component """
    df = None
    if contents is not None:
        df = parse_contents(contents, filename, last_modified).to_json()
    return df
  @app.callback(
    [
        Output('graph', 'style'),
        Output('graph-with-slider', 'figure'),
        Output('year-slider', 'marks'),
        Output('year-slider', 'min'),
        Output('year-slider', 'max'),
        Output('y_dropdown', 'options'),
        Output('x_dropdown', 'options'),
        Output('size_dropdown', 'options'),
        Output('annotation_dropdown', 'options')
    ],
    [
        Input('upload-button', 'n_clicks'),
        Input('year-slider', 'value'),
        Input('y_dropdown', 'value'),
        Input('x_dropdown', 'value'),
        Input('size_dropdown', 'value'),
        Input('annotation_dropdown', 'value')
    ],
    [
        State('hidden-data', 'children')
    ]
  )
  # Function update_figure takes inputs from user to determine x axis, y axis, point size, and annotation
  def update_figure(clicks, selected_year, selected_y, selected_x, selected_size, selected_annotation, df):
    """
    This callback handles updating the graph in response to user actions. All updates must
    pass through this callback. The functionality should be split out into library files
    as it gets more complex.
    """
    # Set default values for when no data has yet been loaded
    year_min = 0
    year_max = 1
    figure = {}
    marks = {}
    style = {'display': 'none'}  # Don't display the graph until data is uploaded
    traces = []
    x_key = ''
    y_key = ''
    size_key = ''
    annotation_key = ''
    y_dropdown_options = []
    x_dropdown_options = []
    size_dropdown_options = []
    annotation_dropdown_options = []
    # If the is data uploaded
    if df is not None:
        df = pd.read_json(df)
        marks_edited =  {str(year) : {'label':str(year), 'style':{'visibility':'hidden'}} for year in df['X'].unique()}
        for update_key in list(marks_edited.keys())[::3]:
        #FIXME: remove float rendering (maybe start with the casting order?)
             marks_edited[str(int(float(update_key)))]['style']['visibility'] = 'visible'
        marks = marks_edited
        year_min = df['X'].min()
        year_max = df['X'].max()
        numeric_df = df.select_dtypes(include='number')
        numeric_df_columns = list(numeric_df.columns)
        y_dropdown_options = [{"label": i, "value": i} for i in numeric_df_columns]
        x_dropdown_options = [{"label": i, "value": i} for i in numeric_df_columns]
        annotation_dropdown_options = [{"label": i, "value": i} for i in df.columns]
        size_dropdown_options = [{"label": i, "value": i} for i in numeric_df_columns]
        if selected_y is not None:
            y_key = selected_y
        else:
            y_key = numeric_df_columns[0]
        if selected_x is not None:
            x_key = selected_x
        else:
            y_key = numeric_df_columns[1]
        if selected_size is not None:
            size_key = selected_size
        else:
            y_key = numeric_df_columns[0]
        if selected_annotation is not None:
            annotation_key = selected_annotation
        else:
            y_key = numeric_df_columns[1]
        # Filtering by year is the only interaction currently support
        if selected_year is None:
            filtered_df = df
        else:
            # Filters to a given x value from the slider
            filtered_df = df[df['X'] == selected_year]
        # Iterates over all 'continents' for a given x value to generate all the bubbles in the graph
        # TODO: Add general handling for other 'contintents' not using the 'name' axis (dropdown/textfield?)
        for i in filtered_df.name.unique():
            df_by_continent = filtered_df[filtered_df['name'] == i]
            traces.append(go.Scatter(
                x=df_by_continent[x_key],
                y=df_by_continent[y_key],
                mode='markers',
                opacity=0.7,
                marker={
                    # The size is determined from the value of the dropdown given for size,
                    # and starts at a default size of 15 with no data and scales
                    'size': list(map(lambda increm: int((50 * (increm/100)) + 15),
                            list(df_by_continent[size_key].fillna(0)))),
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name = i,
                hovertext=df_by_continent[annotation_key].values.tolist()
            ))
        style = {
            'width': '100%'
        }
        figure = {
            'data': traces,
            # Lays out axis types and ranges based on slider slections
            'layout': dict(
                xaxis={
                    'type': 'log',
                    'title': ' '.join(x_key.split('_')).title(),
                    'autorange': 'true'
                },
                yaxis={
                    'title': ' '.join(y_key.split('_')).title(),
                    'autorange': 'true'
                },
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                # Defines transition behaviors
                transition={
                    'duration': 500,
                    'easing': 'cubic-in-out'
                }
            )
        }
    # breakpoint()
    return (style, figure, marks, year_min, year_max,
           y_dropdown_options, x_dropdown_options,
           size_dropdown_options, annotation_dropdown_options)
