from bokeh.plotting import figure, output_file, show

#prepare the data
x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

#output data to file
output_file('lines.html')

#Create plot
p = figure(
    title = "lines_graph", x_axis_label='x', y_axis_label='y')

#Add Line renderer
p.line(x, y, legend = 'Temp', line_width = 2)

#show results
show(p)