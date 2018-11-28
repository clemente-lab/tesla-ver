import lodi
from lodi import parse
import numpy as np
import pandas as pd

def trajectory_to_dataframe(traj):

    columns = traj.get_mdata().keys()
    columns.insert(0, 'time')
    columns.insert(0, 'values')
    dframe_return = dict()
    for val in columns:
        if val == 'time':
            dframe_return['time'] = traj.get_time()
        elif val == 'values':
            dframe_return['values'] = traj.values
        else:
            # Adds all of the other options beyond time and values
            # dframe_return[val] = traj.get_mdata()[val]
            continue
    return pd.DataFrame(dframe_return)