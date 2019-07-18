import os
import json
import itertools

def parse_loclust_string_to_json(loclust_string, file_name):
    jsonDict = dict()

    #Turns string of input into a 2d list
    split_data = map(lambda x: x.split('\t'), loclust_string.split('\n'))

    #adds a dictionary of all of the keys
    jsonDict['keys'] = split_data[0]

    #Reduces the 2d list to just a list of non keys and removes an empty list at the end
    split_data = split_data[1:-1]

    #Creates a list of tuples of the type (ID, dictionary) where the dictionary is key:value for each ID's list
    #of values, and with the special key 'XYData' to store each X:Y pair in a sub-dictionary
    split_data = [id_list_to_dict(split_data_indiv,jsonDict['keys']) for split_data_indiv in split_data]

    #adds the ID:dictionary pairs from each tuple
    for id_chunk in split_data:
        id_val, dict_val = id_chunk
        jsonDict[id_val] = dict_val
    if not os.path.exists('./assets/json_data/db.json'):
        with open("./assets/json_data/db.json", "w") as write_file:
            json.dump(jsonDict, write_file)
    
def id_list_to_dict(id_list, keys_list):
    id_dict = dict()

    #Populates X:Y pairs of sub dictionary
    id_dict['XYData'] = {str(key):str(value) for key, value in zip(id_list[1].split(','), id_list[2].split(','))}
    #Creates dictionary of all key:idvalue pairs, now including the XYData
    id_dict.update({str(key):str(value) for key, value in zip(keys_list[3:], id_list[3:])})
    #Returns a tuple with the original ID and the new dictionary corresponding to that ID
    return (id_list[0],id_dict)
def get_X_and_Y():
    holding_dict = dict()
    with open('./assets/json_data/db.json', 'r') as read_file:
        holding_dict = json.load(read_file)
    # value = 
        return {'X':sorted(map(lambda to_int: int(to_int),set(
        itertools.chain.from_iterable([id_chunk.get('XYData').keys() 
        for id_chunk in 
        [id_entry for id_entry in holding_dict.values()][1:]])))),

        'Y':sorted(map(lambda to_float: float(to_float),set(itertools.chain.from_iterable(
        [id_chunk.get('XYData').values() 
        for id_chunk in 
        [id_entry for id_entry in holding_dict.values()][1:]]))))
        }

def removed(remove_list, item):
    remove_list.remove(item)
    return remove_list

def get_keys_metadata():
    holding_dict = dict()
    with open('./assets/json_data/db.json', 'r') as read_file:
        holding_dict = json.load(read_file)
    return removed(holding_dict.values()[1].keys(), 'XYData')
