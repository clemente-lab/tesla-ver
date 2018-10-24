#Imports the main plotly library and the graphing library
import plotly.plotly as py
import plotly.graph_objs as go

#Creates a scatterplot from the selected values
trace0 = go.Scatter(
    x=[1, 2, 3, 4],
    y=[10, 15, 13, 17]
)
trace1 = go.Scatter(
    x=[1, 2, 3, 4],
    y=[16, 5, 11, 9]
)

#Creates a list, data, made of the two scatterplots trace0 and trace1
data = [trace0, trace1]

#Creates a graph using the data variable, called 'basic-line', on the server (username and api key connected during setup)
py.iplot(data, filename = 'basic-line')