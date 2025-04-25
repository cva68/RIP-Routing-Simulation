"""
    Context imports for unit tests
    Modified from: https://github.com/navdeep-G/samplemod (BSD2)
"""

# Ignore this file from flake8 - it is used to set up the test environment
# flake8: noqa

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from ripd._structures import *
from ripd._configloader import ConfigLoader
from ripd.ripd import RIPDaemon
from ripd._interface import Interface
from ripd._table import *
