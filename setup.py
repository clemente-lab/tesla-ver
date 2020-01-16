from __future__ import division

from setuptools import setup
from glob import glob
import ast
import re

__author__ = "The Clemente Lab"
__copyright__ = "Copyright (c) 2018 The Clemente Lab"
__credits__ = ['Alexander Kyimpopkin', 'David Wallach', 'Jose C. Clemente']
__license__ = "GPL"
__maintainer__ = "Alexander Kyimpopkin"
__email__ = "alexanderkyim@gmail.com"

_version_re = re.compile(r'__version__\s += \s+(.*)')

with open('tesla_ver/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name = 'tesla_ver',
    version = version,
    description = 'TimE Series Longitudinal Analysis Server',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    url = 'http://github.com/clemente-lab/tesla-ver',
    author = __author__,
    author_email = __email__,
    license = __license__,
    packages = ['tesla_ver'],
    scripts = glob('scripts/*py'),
    install_requires = [
        'numpy',
        'dash',
        'dash_html_components',
        'dash_core_components',
        'plotly',
        'pandas',
        'dash_renderer',
        'flask',
    ],
    entry_points = {
        'console_scripts': [
            'run = wsgi:main',
        ]},
    zip_safe = False)
