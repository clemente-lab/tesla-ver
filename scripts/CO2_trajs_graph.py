import plotly as plty
import plotly.graph_objs
import time
import csv
import os

#How does one select the C02_trajs.csv file from the data directory?
with open('/data/CO2_trajs', 'r') as main_csv:
    reader = csv.reader(main_csv)
    for row in reader:
        print (row)


