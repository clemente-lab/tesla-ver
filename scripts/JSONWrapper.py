import json
import os
import logging

class JSONWrapper(object):
    logging.basicConfig(filename='./logs/JSON_Wrapper.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
    def __init__(self, path_to_json):
        self.path_to_json = path_to_json
        self.json_container = self.set_json(path_to_json)
        
    def get_json(self):
        return self.json_container
    
    def reset_json(self):
        self.__init__(self.path_to_json)

    def set_json(self, new_path_to_json):
        if os.path.isfile(new_path_to_json):
            with open(new_path_to_json, 'r') as f:
                self.json_container = json.load(f)
                logging.info('Opened JSON File')
            if '0' in self.json_container.keys():
                pass
            else:
                logging.debug(self.json_container.keys())
                raise JSONContainerEmpty

class JSONContainerEmpty(Exception):
    def __init__(self, msg):
        self.msg = msg
    