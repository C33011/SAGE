"""
SAGE data package.

This package provides functionality for loading, profiling, and analyzing data
from various sources.
"""

from sage.data.loader import load_data
from sage.data.profiler import profile_dataframe

# List of functions to expose when using `from sage.data import *`
__all__ = [
    'load_data',
    'profile_dataframe'
]
