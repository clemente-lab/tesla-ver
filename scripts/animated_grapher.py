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
    main_data = Grid([Column(dtfr[column_name], column_name) for column_name in dtfr.columns])
    py.grid_ops.upload(main_data, 'anim_grid'+str(time.time), auto_open=False)
    figure = {
        'data': [],
        'layout': {},
        'frames': [],
        'config': {'scrollzoom': True}
    }

    figure['layout']['xaxis'] = {'range': [min(dtfr[0]), max(dtfr[0])], 'title': xaxis_title, 'gridcolor': '#FFFFFF'}
    figure['layout']['yaxis'] = {'title': yaxis_title, 'range': [np.nanmin(dtfr), np.nanmax(dtfr[:, 1:])]}
    }
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
                    'args': [None, {'frame': {'duration': 500, 'redraw': False},
                                    'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                                      'transition': {'duration': 0}}],
                    'label': 'Pause',
                    'method': 'animate'
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }
    ]

    for counter in list(range(len(main_data.__len__))):
        data_dict = {
            'xsrc': main_data.get_column_reference('xvalues'),
            'ysrc': main_data.get_column_reference('yvalues'+str(counter)),
            'mode': 'markers',
            'marker': {
                'sizemode' : 'area',
                'sizeref' : 200000
            }
        }
        figure['data'].append(data_dict)
animate_trajectories('../teslaver/data/CO2_trajs.csv', 'testyboi', 'time', 'values', 'spicy bois')
