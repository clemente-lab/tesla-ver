import lodi
from lodi import parse
import numpy as np
import pandas as pd
import plotly.plotly as py
import plotly.figure_factory as ff
from plotly.grid_objs import Grid, Column


def trajectory_to_grid(path, yaxis):
    trajectory = lodi.parse.read_trajectories(path)
    columns_list = list()
    for traj in trajectory:
        #makes list of all potential time values  
        xvalues = traj.time
        #TODO: Sort them into order
    # columns_list.append('xavlues')
    # values_list = np.empty(shape = (len(xvalues), len(trajectory)))
    return_frame = pd.DataFrame({'xvalues': xvalues})
    for num, traj in enumerate(trajectory):
        #Checks whether or not yaxis is mdata, and assigns appropriate data to the lists
        if yaxis == 'values':
            yvalues = traj.values
            while(len(yvalues) < len(xvalues)):
                yvalues = np.insert(yvalues, 0, None)
            columns_list.append('yvalues' + str(num))
            data_main = {columns_list[num]: yvalues}
            df_joined = pd.DataFrame(data=data_main)
            return_frame = return_frame.join(df_joined)
        elif yaxis in traj.get_mdata():
            yvalues = traj.get_mdata()[yaxis]
            while(len(yvalues) < len(xvalues)):
                yvalues = np.insert(yvalues, 0, None)
            columns_list.append(str(yaxis) + 'values' + str(num))
            data_main = {columns_list[num]: yvalues}
            df_joined = pd.DataFrame(data=data_main)
            return_frame = return_frame.join(df_joined)
        else:
            print 'Invalid Yaxis input'
            exit
    grid = Grid([Column(return_frame[column_name], column_name) for column_name in return_frame.columns])
    return grid
    
print trajectory_to_grid('../teslaver/data/CO2_trajs.csv', 'country-code')