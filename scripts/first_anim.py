import plotly.plotly as plty
from plotly.grid_objs import Grid, Column

import time

column_1 = Column([0.5], 'x')
column_2 = Column([0.5], 'y')
column_3 = Column([1.5], 'x2')
column_4 = Column([1.5], 'y2')
column_5 = Column([2.0], 'x3')
column_6 = Column([3.0], 'y3')

grid = Grid([column_1, column_2, column_3, column_4, column_5, column_6])
plty.grid_ops.upload(grid, 'tut_anim'+str(time.time()), auto_open = False)

figure = {
    'data': [
        {
            'xsrc': grid.get_column_reference('x3'),
            'ysrc': grid.get_column_reference('y3'),
            'mode': 'markers',
        }
    ],
    'layout': {'title': 'Ping Pong Animation',
               'xaxis': {'range': [0, 2], 'autorange': False},
               'yaxis': {'range': [0, 2], 'autorange': False},
               'updatemenus': [{
                   'buttons': [
                       {'args': [None],
                        'label': 'Play',
                        'method': 'animate'}
               ],
               'pad': {'r': 10, 't': 87},
               'showactive': False,
               'type': 'buttons'
                }]},
    'frames': [
        {
            'data': [
                {
                    'xsrc': grid.get_column_reference('x'),
                    'ysrc': grid.get_column_reference('y'),
                    'mode': 'markers',
                }
            ]
        },
        {
            'data': [
                {
                    'xsrc': grid.get_column_reference('x2'),
                    'ysrc': grid.get_column_reference('y2'),
                    'mode': 'markers',
                }
            ]
        },
        {
            'data': [
                {
                    'xsrc': grid.get_column_reference('x3'),
                    'ysrc': grid.get_column_reference('y3'),
                    'mode': 'markers',
                }
            ]
        },
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

plty.icreate_animations(figure, 'tut_anim'+str(time.time()))