#!/usr/bin/env python
from __future__ import division

import click
from teslaver import __version__

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)

def test():
    """ Test
    """
                              
if __name__ == "__main__":
    test()
