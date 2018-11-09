import plotly.plotly as py
import plotly.graph_objs as go
import time
import lodi
from lodi import parse

#imports the dataset and parses it with the lodi parse method
parsed_data = lodi.parse.read_trajectories('../teslaver/data/CO2_trajs.csv')


print parsed_data[0].time

#Creats list to store all traced scatterplots
data = list()

#Iterates through the entire dataset and creates traces out of the data
for counter in list(range(len(parsed_data))):
    #Creates each traced scatterplot
    trace = go.Scattergl(
        x = parsed_data[counter].time,
        y = parsed_data[counter].values,
        mode = 'lines+markers',
        name= parsed_data[counter].get_mdata()['country_name']
     )
     #Appends each traced scatterplot to data list
    data.append(trace)

#Creates layout of the graph
layout= go.Layout(
    title= 'C02 Trajectories',
    hovermode= 'closest',
    xaxis= dict(
        title= 'Year',
        autorange = True,
        ticklen= 5,
        zeroline= False,
        gridwidth= 2,
    ),
    yaxis=dict(
        title= 'Carbon Dioxide in Kg Per Dollar per capita per person',
        autorange = True,
        ticklen= 5,
        gridwidth= 2,
    ),
    showlegend= True
)

#Creates figure containing both the data and layout, ready to graph
fig = go.Figure(data=data, layout=layout)

#Plots the data on plotly
py.plot(fig, filename = 'C02_Graph'+str(time.time()))