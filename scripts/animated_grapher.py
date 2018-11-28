import lodi
from lodi import parse
import plotly.plotly as py
import plotly.figure_factory as ff
from plotly.grid_objs import Grid, Column
import numpy as np
import pandas as pd
import trajectory_to_dataframe

class animate_trajectories:

    def __init__(self, path, graph_title, xaxis_title, yaxis_title, trajectory_title):
        self.grid = animate_trajectories.grid_generator(self, path)
        self.graph_title = graph_title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.path = path
        print self.grid
        # animate_trajectories.generate_grids_and_anim(self)

    def generate_grids_and_anim(self):
        py.grid_ops.upload(self.grid, self.graph_title, auto_open=False)

    def grid_generator(self, path):
        #TODO:build grid generator  Use pandas dataframe with FF?

        trajectories = lodi.parse.read_trajectories(path)

        #Creates list to store all traced scatterplots
        data = list()

        #Iterates through the entire dataset
        for traj in trajectories:
            
            