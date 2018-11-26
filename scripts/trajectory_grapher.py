import plotly.plotly as py
import plotly.graph_objs as go
import time
import lodi
from lodi import parse

def graph_trajectories(path, graph_title, xaxis_title, yaxis_title, trajectory_name):
    """Graphs a longitudinal dataset on plotly:

    Args:
        path: the path to the dataset
        graph_title: the title for top of the graph
        xaxis_title: the x-axis title
        yaxis_title: the y-axis title
        trajectory_name: the name for each plotted line/trajectory
    """

    #imports the dataset and parses it with the lodi parse method
    trajectories = lodi.parse.read_trajectories(path)

    #Creates list to store all traced scatterplots
    data = list()

    #Iterates through the entire dataset and creates traces out of the data
    for traj in trajectories:
        
        #Checks whether or not xaxis_title is mdata, and assigns appropriate data to the lists
        if xaxis_title == 'time':
            x_values = traj.time
        elif xaxis_title in traj.get_mdata():
            x_values = list(map(float, traj.get_mdata()[xaxis_title]))
        else:
            print 'Invalid Xaxis input'
            exit
        
        #Checks whether or not yaxis_title is mdata, and assigns appropriate data to the lists
        if yaxis_title == 'values':
            y_values = traj.values
        elif yaxis_title in traj.get_mdata():
            y_values = list(map(float, traj.get_mdata()[yaxis_title]))
        else:
            print 'Invalid Yaxis input'
            exit
        
        trace = go.Scattergl(
                    x = x_values,
                    y = y_values,
                    mode = 'lines+markers',
                    name= traj.get_mdata()[trajectory_name]
                )
        #Appends each traced scatterplot to data list
        data.append(trace)

    #Creates layout of the graph
    layout= go.Layout(
        title= graph_title + ' ' + str(time.time()),
        hovermode= 'closest',
        xaxis= dict(
            title= xaxis_title,
            autorange = True,
            ticklen= 5,
            zeroline= False,
            gridwidth= 2,
        ),
        yaxis=dict(
            title= yaxis_title,
            autorange = True,
            ticklen= 5,
            gridwidth= 2,
        ),
        showlegend= True
    )

    #Creates figure containing both the data and layout, ready to graph
    fig = go.Figure(data=data, layout=layout)

    #Plots the data on plotly
    py.plot(fig, filename = graph_title)