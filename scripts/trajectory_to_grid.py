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
    columns_list.append('xavlues')
    values_list = np.empty(shape = (len(xvalues), len(trajectory)))
    for num, traj in enumerate(trajectory):
        #Checks whether or not yaxis is mdata, and assigns appropriate data to the lists
        if yaxis == 'values':
            #supposed to return a list where if a year doesnt overlap, contains a true values, and otherwise has a false value,
            #from there, theres a loop to basically iterate through that trajectory, and puts the value for a class
            none_list = np.isin(traj.time, xvalues, True, True)
            #
            print none_list
            yvalues = list(traj.values)
            yvalues_populated = list()
            for val in none_list:
                if val:
                    yvalues_populated.append(val)
                else:
                    yvalues_populated.append(None)
            print yvalues_populated
            values_list[:, num] = yvalues_populated
            columns_list.append('yvalues' + str(num))
        elif yaxis in traj.get_mdata():
            yvalues = list(map(float, traj.get_mdata()[yaxis]))
            none_list = np.in1d(traj.time, xvalues, True, True)
            yvalues_populated = list()
            for val in none_list:
                if val in yvalues:
                    yvalues_populated.append(val)
                else:
                    yvalues.append(None)
            values_list.append(yvalues_populated)
            columns_list.append('yvalues' + str(num))
        else:
            print 'Invalid Yaxis input'
            exit
    return values_list
    #TODO: Create code to insert None values in between all values which arent set up correctly
    # dframe_return = pd.DataFrame(values_list, columns=columns_list)
    # columns_list2 = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']
    # np1 = np.hstack([[1,2,3],[4,5,6],[7,8,9]])
    # np2 = np.hstack([[1,2,3],[4,5,None],[7,8,9]])
    # combined = np.vstack((np1, np2)).T
    # return pd.DataFrame(combined, columns = ['1st', '2nd'])
    
print trajectory_to_grid('../teslaver/data/CO2_trajs.csv', 'values')