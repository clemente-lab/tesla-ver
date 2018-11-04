import plotly as plty
import plotly.graph_objs
import time
import csv
import os

#How does one select the C02_trajs.csv file from the data directory?
with open('./data/CO2_trajs.csv', 'r') as main_csv:
    main_list = list(csv.reader(main_csv))

    

    #separate all of the list entries into their own sections (id and first year no longer in same entry)
    for counter in list(range(len(main_list))):
            main_list[counter] = "\t".join(main_list[counter]).split()

            temp_year_list = list()
            temp_kg_list = list()
            val_indicies_to_remove = list()
            #Clump the x values (years) into their own sublist and the y values as well, across all lists
            for val in main_list[counter]:
                # puts x values into their own list
                if val.startswith('20') or val.startswith('19'):
                    temp_year_list.append(val)
                    val_indicies_to_remove.append(val)
                #puts y values into their own list
                if val.startswith('0.'):
                    temp_kg_list.append(val)
                    val_indicies_to_remove.append(val)
            for val in val_indicies_to_remove:
                main_list[counter].remove(val)
            #Replaces the new list versions of the year values into the lists at the appropriate indicies
            main_list[counter].insert(1, temp_year_list)
            main_list[counter].insert(2, temp_kg_list)


    



# print(temp_kg_list)
print(main_list[185])