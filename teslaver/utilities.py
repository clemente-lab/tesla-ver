from pandas import DataFrame, concat


def trajectories_to_dataframe(trajs):
    """
    A function for converting a list of trajectories into a pandas DataFrame.
    ========================================================================
    :trajs: A list of trajectories to convert.
    """
    traj_frames = []
    # For each trajectory
    for traj in trajs:
        # Store the X and Y values in a dictionary
        traj_data = {
            'ID': [traj.get_ID() for i in range(len(traj.get_time()))],
            'X': traj.get_time(),
            'Y': traj.get_values()
        }
        # Add each metadata entry to the dictionary
        for key in traj.get_mdata().keys():
            print(traj.get_mdata()[key])
            # If there is only a single value, repeat it for each time point
            # To do this check if the result is not a list
            if not traj.get_mdata()[key] is list:
                traj_data[key] = [traj.get_mdata()[key] for i in range(len(traj_data['X']))]
            # Or if there are several values but not enough for each time point, use the first value
            elif len(traj.get_mdata()[key]) < len(traj_data['X']):
                traj_data[key] = [traj.get_mdata()[key][0] for i in range(len(traj_data['X']))]
            # Or if there are values for each time point store them as is
            elif len(traj.get_mdata()[key]) == len(traj_data['X']):
                traj_data[key] = traj.get_mdata()[key]
        # Create a dataframe from the dictionary
        df = DataFrame(traj_data)
        traj_frames.append(df)
    # Concatenate all the dataframes into a single frame
    all_trajs = concat(traj_frames)
    return all_trajs
