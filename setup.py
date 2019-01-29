#!/usr/bin/env python

from __future__ import division

from setuptools import setup
from glob import glob
import ast
import re

__author__ = "The Clemente Lab"
__copyright__ = "Copyright (c) 2018 The Clemente Lab"
__credits__ = ["Jose C. Clemente"]
__license__ = "GPL"
__maintainer__ = "Jose C. Clemente"
__email__ = "jose.clemente@gmail.com"

# https://github.com/mitsuhiko/flask/blob/master/setup.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('teslaver/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(name='teslaver',
      version=version,
      description='TimE Series Longitudinal Analaysis Server',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
      ],
      url='http://github.com/clemente-lab/teslaver',
      author=__author__,
      author_email=__email__,
      license=__license__,
      packages=['teslaver'],
      scripts=glob('scripts/*py'),
      install_requires=[
          'numpy',
          'scipy',
          'click',
          'seaborn',
          'sklearn',
          'pandas'
      ],
      zip_safe=False)
