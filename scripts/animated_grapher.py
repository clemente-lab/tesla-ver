import lodi
from lodi import parse
import plotly.plotly as py
import numpy as np
import pandas as pd
import trajectory_to_grid as ttg
import time
import utilities as utls
import plotly.graph_objs as go
from plotly.grid_objs import Grid, Column
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


def animate_trajectories(path, graph_title, xaxis_title, yaxis_title, trajectory_title):
    # This add every data point to every year which isn't what we want
    parsed_dataframe = utls.trajectories_to_dataframe(lodi.parse.read_trajectories(path))
    figure = {
        'data': [],
        'layout': {},
        'frames': [],   
        'config': {'scrollzoom': True}
    }

    # Use pandas dataframe methods to get min/max values
    #I'm a bit unsure how to pull the correct values from the dataframe.
    figure['layout']['xaxis'] = {'range': [parsed_dataframe['X'].min(), parsed_dataframe['X'].max()],
                                 'title': xaxis_title,
                                 'gridcolor': '#FFFFFF'}
    figure['layout']['yaxis'] = {'title': yaxis_title,
                                 'range': [
                                     parsed_dataframe.filter(regex='Y*').min(),
                                     parsed_dataframe.filter(regex='Y*').max()
                                 ]}
    # Get a list of yvalues to track
    all_cols = list(filter(lambda x: 'yvalue' in x, dtfr.columns))

    sliders_dict = {
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Year:',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': []
    }

    figure['layout']['updatemenus'] = [
        {
            'buttons': [
                {
                    'args': [
                        None,
                        {
                            'frame': {
                                'duration': 500,
                                'redraw': False
                            },
                            'fromcurrent': True,
                            'transition': {
                                'duration': 300,
                                'easing': 'quadratic-in-out'
                            }
                        }
                    ],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 0,
                                                'redraw': False},
                                      'mode': 'immediate',
                                      'transition': {'duration': 0}}],
                    'label': 'Pause',
                    'method': 'animate'
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': True,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }
    ]

    # Iterate through the desired columns
    for col in all_cols:
        data_dict = {
            'xsrc': parsed_dataframe.get_column_reference('xvalues'),
            'ysrc': parsed_dataframe.get_column_reference(col),
            'mode': 'markers',
            'marker': {
                'sizemode': 'area',
                'sizeref': 200000
            }
        }
        figure['data'].append(data_dict)

    # Create each frame of the animation
    # How do I separate the data by column
    for year in parsed_dataframe['X']:
        frame = {
            'data': [],
            'name': str(year)
        }
        # Add the value of each column for the current frame
        for col in all_cols:
            data_dict = {
                'xsrc': parsed_dataframe.get_column_reference('xvalues'),
                'ysrc': parsed_dataframe.get_column_reference(col),
                'mode': 'markers',
                'marker': {
                    'sizemode': 'area',
                    'sizeref': 200000
                },
                'name': col
            }
            frame['data'].append(data_dict)

        # Add the frame to the figure
        figure['frames'].append(frame)
        slider_step = {'args': [
            [year],
            {'frame': {'duration': 300, 'redraw': False},
             'mode': 'immediate',
             'transition': {'duration': 300}}
        ],
            'label': year,
            'method': 'animate'}
        sliders_dict['steps'].append(slider_step)

    figure['layout']['sliders'] = [sliders_dict]
    return url, figure


url, figure = animate_trajectories('../teslaver/data/CO2_trajs_short.csv', 'testyboi', 'time', 'values', 'spicy bois')
url2 = py.icreate_animations(figure, 'anim_grid'+str(time.time()))
# Print the url of the animated plot
print(url2.resource)
