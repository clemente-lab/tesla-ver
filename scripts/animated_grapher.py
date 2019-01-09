import lodi
from lodi import parse
import plotly.plotly as py
import numpy as np
import pandas as pd
import trajectory_to_grid as ttg
import time
import plotly.graph_objs as go
from plotly.grid_objs import Grid, Column

def animate_trajectories(path, graph_title, xaxis_title, yaxis_title, trajectory_title):
    main_data = ttg.trajectory_to_grid(path, yaxis_title)
    py.grid_ops.upload(main_data, 'anim_grid'+str(time.time), auto_open=False)
    for counter in list(range(len(main_data.__len__))):
        figure = {}
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