import pandas as pd
import numpy as np


def upload_string_to_df(upload_string, filename):
    # Splits input string into lists of strings, one per trajectory
    split_string_list = list(map(lambda entry: entry.split("\t"), upload_string.split("\n")[:-1]))
    split_updated = list()
    # Splits the numerical (X, Y) values in each trajectory list into their own sub lists
    for split_entry in split_string_list[1:]:
        split_updated.append(
            [
                np.array(split_check.split(",")).astype(np.float64)
                if "," in split_check and test_float_cast(split_check)
                else split_check
                for split_check in split_entry
            ]
        )
    # Generate Dataframe from lists
    string_frame = pd.DataFrame(data=split_updated, columns=split_string_list[0])
    # Generate number of repeated indicies for each list(X list and Y list)
    explode_indicies = string_frame.index.repeat(string_frame["X"].str.len())
    # Merge X and Y flattened frames
    string_frame_exploded = pd.concat(
        [pd.DataFrame({expand_values: np.concatenate(string_frame[expand_values]) for expand_values in ["X", "Y"]})],
        axis=1,
    )
    # Reindex new frame from merged
    string_frame_exploded.index = explode_indicies
    # Merge exploded frames with old metadata
    string_frame_exploded = string_frame_exploded.join(string_frame.drop(["X", "Y"], axis=1), how="left")
    # Renames column
    string_frame_exploded = string_frame_exploded.rename(columns={"Y": filename + "_data"})
    return string_frame_exploded


# Checks if string can be cast to a list of numpy float64's
def test_float_cast(chck_string):
    if "," in chck_string:
        split_temp = np.array(chck_string.split(","))
        try:
            split_temp.astype(np.float64)
            return True
        except:
            return False
    else:
        return False
