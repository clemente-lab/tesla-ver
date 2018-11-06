import plotly.plotly as py
import plotly.graph_objs as go
import time
import csv
import os
import lodi
from lodi import parse

#imports the dataset and parses it with the lodi parse method
parsed_data = lodi.parse.read_csv('../teslaver/data/CO2_trajs.csv')

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

data = list()

for counter in list(range(len(parsed_data['ID']))):
    trace = go.Scattergl(
        x = parsed_data['X'],
        y = parsed_data['Y'],
        mode = 'lines+markers',
        text = parsed_data['']
     )
    data.append(trace)
py.iplot(data, filename = 'C02_Graph '+str(time.time()))
# #How does one select the C02_trajs.csv file from the data directory?
# with open('./data/CO2_trajs.csv', 'r') as main_csv:
#     main_list = list(csv.reader(main_csv))
#     #separate all of the list entries into their own sections (id and first year no longer in same entry)
#     for counter in list(range(len(main_list))):
#             main_list[counter] = "\t".join(main_list[counter]).split()
#             temp_year_list = list()
#             temp_kg_list = list()
#             val_indicies_to_remove = list()
#             #Clump the x values (years) into their own sublist and the y values as well, across all lists
#             for val in main_list[counter]:
#                 # puts x values into their own list
#                 if len(val) == 4 and (val.startswith('20') or val.startswith('19')):
#                     temp_year_list.append(val)
#                     val_indicies_to_remove.append(val)
#                 #puts y values into their own list
#                 if val.startswith('0.'):
#                     temp_kg_list.append(val)
#                     val_indicies_to_remove.append(val)
#             for val in val_indicies_to_remove:
#                 main_list[counter].remove(val)
#             #Replaces the new list versions of the year values into the lists at the appropriate indicies
#             main_list[counter].insert(1, temp_year_list)
#             main_list[counter].insert(2, temp_kg_list)
# data = list()
# #Adds each plot to trace to a list
# for counter in list(range(len(main_list))):
#     trace = go.Scattergl(
#         x = main_list[counter][1],
#         y = main_list[counter][2],
#         mode = 'lines+markers',
#         #Imperfectly adds the labels to each country's graph
#         text=main_list[counter][len(main_list[counter])-21]

#     )
#     data.append(trace)
#Plots data
