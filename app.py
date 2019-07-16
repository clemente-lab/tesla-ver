# -*- coding: utf-8 -*-
"""
Created On Friday July 1

@author: alexanderkyim
"""

import dash

app = dash.Dash(__name__)

server = app.server

app.config.supress_callback_exceptions = True