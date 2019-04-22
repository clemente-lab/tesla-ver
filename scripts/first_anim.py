#imports the main plotly library as plty
import plotly.plotly as plty
#imports the Grid and Column objects from grid_objects
from plotly.grid_objs import Grid, Column
import time

#Datapoints for movement
column_1 = Column([0.5], 'x')
column_2 = Column([0.5], 'y')
column_3 = Column([1.5], 'x2')
column_4 = Column([1.5], 'y2')
column_5 = Column([2.0], 'x3')
column_6 = Column([3.0], 'y3')

#Creates a variable called grid, which is a new Grid comprised of the 6 column variables
grid = Grid([column_1, column_2, column_3, column_4, column_5, column_6])
#Creates a new graph grid on the server, named tut_anim, without opening it and comprised of the Grid grid
plty.grid_ops.upload(grid, 'tut_anim'+str(time.time()), auto_open = False)

#Creates the animation
figure = {
    #Defines the starting point for the animation
    'data': [
        {
            'xsrc': grid.get_column_reference('x3'),
            'ysrc': grid.get_column_reference('y3'),
            'mode': 'markers',
        }
    ],
    #Defines the layout, where the initial range shown, the title, and any buttons are defined.
    'layout': {
                'title': 'Ping Pong Animation',
                'xaxis': {'range': [0, 2], 'autorange': False},
                'yaxis': {'range': [0, 2], 'autorange': False},
                'updatemenus': [{
                   'buttons': [
                       {
                            'args': [None],
                            'label': 'Play',
                            'method': 'animate'
                    }
                ],
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons'
                }]},
    #Creates the different frames of the animation
    'frames': [
        {
            #Animation Frame 1, indicates the position to move the point to
            'data': [
                {
                    'xsrc': grid.get_column_reference('x'),
                    'ysrc': grid.get_column_reference('y'),
                    'mode': 'markers',
                }
            ]
        },
        #Animation Frame 2, see Animation Frame 1 comment for explanation
        {
            'data': [
                {
                    'xsrc': grid.get_column_reference('x2'),
                    'ysrc': grid.get_column_reference('y2'),
                    'mode': 'markers',
                    #Sets the color and size of the point
                    'marker': {'color': '#5405e5', 'size': 25}
                }
            ]
        },
        {
            #Animation Frame 3
            'data': [
                {
                    'xsrc': grid.get_column_reference('x3'),
                    'ysrc': grid.get_column_reference('y3'),
                    'mode': 'markers',
                    'marker': {'color': '#000000', 'size': 50}
                }
            ]
        },
        #Animation Frame 4
        {
            'data': [
                {
                    'xsrc': grid.get_column_reference('x'),
                    'ysrc': grid.get_column_reference('y'),
                    'mode': 'markers',
                }
            ]
        }
    ]
}

#Creates the animation on the server, with the title 'tut_anim' + the current time, using the animation frames defined in 'figure'
plty.create_animations(figure, 'tut_anim'+str(time.time()))