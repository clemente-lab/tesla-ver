import plotly.plotly as py
import plotly.graph_objs as go
import time
import lodi
from lodi import parse

def graph_trajectories(path, graph_title, xaxis_title, yaxis_title):
    """Graphs a longitudinal dataset on plotly:

    Args:
        path: the path to the dataset
        graph_title: the title for top of the graph
        xaxis_title: the x-axis title
        yaxis_title: the y-axis title

    """

    #imports the dataset and parses it with the lodi parse method
    trajectories = lodi.parse.read_trajectories(path)

    #Creats list to store all traced scatterplots
    data = list()

    #Iterates through the entire dataset and creates traces out of the data
    for traj in trajectories:
        #Creates each traced scatterplot
        trace = go.Scattergl(
            x = traj.time,
            y = traj.values,
            mode = 'lines+markers',
            name= traj.get_mdata()['country_name']
        )
        #Appends each traced scatterplot to data list
        data.append(trace)

    #Creates layout of the graph
    layout= go.Layout(
        title= xaxis_title,
        hovermode= 'closest',
        xaxis= dict(
            title= 'Year',
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