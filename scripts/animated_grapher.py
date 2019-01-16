import loclust
from loclust import parse
import plotly.plotly as py
import numpy as np
import pandas as pd
import trajectory_to_grid as ttg
import time
import plotly.graph_objs as go
from plotly.grid_objs import Grid, Column


def animate_trajectories(path, graph_title, xaxis_title, yaxis_title, trajectory_title):
    dtfr = ttg.trajectory_to_grid(path, yaxis_title)
    # This add every data point to every year which isn't what we want
    main_data = Grid([Column(dtfr[column_name], column_name) for column_name in dtfr.columns])
    url = py.grid_ops.upload(main_data, 'anim_grid'+str(time.time()), auto_open=False)
    figure = {
        'data': [],
        'layout': {},
        'frames': [],
        'config': {'scrollzoom': True}
    }

    # Use pandas dataframe methods to get min/max values
    figure['layout']['xaxis'] = {'range': [dtfr['xvalues'].min(), dtfr['xvalues'].max()],
                                 'title': xaxis_title,
                                 'gridcolor': '#FFFFFF'}
    figure['layout']['yaxis'] = {'title': yaxis_title,
                                 'range': [
                                     dtfr.filter(regex='yvalues*').min(),
                                     dtfr.filter(regex='yvalues*').max()
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
            'xsrc': main_data.get_column_reference('xvalues'),
            'ysrc': main_data.get_column_reference(col),
            'mode': 'markers',
            'marker': {
                'sizemode': 'area',
                'sizeref': 200000
            }
        }
        figure['data'].append(data_dict)

    # Create each frame of the animation
    for year in dtfr['xvalues']:
        frame = {
            'data': [],
            'name': str(year)
        }
        # Add the value of each column for the current frame
        for col in all_cols:
            data_dict = {
                'xsrc': main_data.get_column_reference('xvalues'),
                'ysrc': main_data.get_column_reference(col),
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
