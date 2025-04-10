"""
SAGE reports package.

This package provides functionality for generating reports and visualizations
from data quality assessment results.
"""

from sage.reports.generator import generate_html_report

# List of functions to expose when using `from sage.reports import *`
__all__ = [
    'generate_html_report'
]
