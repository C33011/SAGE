"""
SAGE configuration package.

This package provides functionality for loading and managing
configuration settings for SAGE.
"""

from sage.config.settings import (
    load_configuration,
    validate_configuration,
    get_default_configuration,
    merge_configurations
)

# List of functions to expose when using `from sage.config import *`
__all__ = [
    'load_configuration',
    'validate_configuration',
    'get_default_configuration',
    'merge_configurations'
]
