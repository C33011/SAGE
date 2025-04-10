"""
SAGE utilities package.

This package provides common utility functions and helpers used across SAGE.
"""

from sage.utils.helpers import (
    safe_divide,
    get_data_type_summary,
    format_number,
    truncate_string,
    get_file_info,
    format_file_size,
    validate_file_exists,
    normalize_column_names,
    is_empty_value
)

from sage.utils.template_engine import TemplateEngine

# List of functions to expose when using `from sage.utils import *`
__all__ = [
    'safe_divide',
    'get_data_type_summary',
    'format_number',
    'truncate_string',
    'get_file_info',
    'format_file_size',
    'validate_file_exists',
    'normalize_column_names',
    'is_empty_value',
    'TemplateEngine'
]
