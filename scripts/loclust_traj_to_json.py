import numpy as np
import pandas as pd
import loclust.parse as parse
import logging
import json
from teslaver import utilities
from itertools import izip as zip

#Logging setup
logging.basicConfig(filename='./logs/raj_to_json.log', filemdoe='a', filepathformat='%(asctime)s - %(message)s', level=logging.INFO)


def traj_to_json(path_to_file, filename='default'):
    df = utilities.trajectories_to_dataframe(parse.read_trajectories(path_to_file))
    groo_ID = df.groupby('ID')
    temp_store = dict()
    #Iterate Over all groups to create JSON Dictionary
    for id_key in groo_ID.groups.keys():
        temp_store[id_key] = dict()
        group_fetched = groo_ID.get_group(id_key)
        keys = list()
        #Creates list of keys for dictionary and then assigns values to it (until 30)
        for key in df.keys():
            if key != 'ID' and key != 'X' and key != 'Y':
                keys.append(key)
        
        for key in keys:
            temp_store[id_key][key] = list(map(lambda x: str(x), group_fetched[key]))
        
        temp_store[id_key]['XYdata'] = {str(key):str(value) for key, value in zip(group_fetched['X'],group_fetched['Y'])}
    try:
            assert len(temp_store.keys()) == len(groo_ID.groups.keys())
            logging.debug('Keys in JSON Dict are the right length')
    except AssertionError:
            logging.error('ID Keys not unique or Not Represented')
            logging.debug(keys)   
    with open("./assets/json_data/{}.json".format(filename), "w") as write_file:
        json.dump(temp_store, write_file)
        logging.info('Wrote JSON')
    return filename
# traj_to_json('./assets/data_source/MicrobiomeMaturation_all_taxa.csv','Ballaboosta')
