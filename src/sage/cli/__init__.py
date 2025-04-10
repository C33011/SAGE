"""
SAGE command-line interface package.

This package provides the command-line interface for running SAGE
data quality assessments and generating reports.
"""

from sage.cli.commands import main, run_assessment, generate_report
from sage.cli.formatters import format_output, print_result, print_table

# List of functions to expose when using `from sage.cli import *`
__all__ = [
    'main',
    'run_assessment',
    'generate_report',
    'format_output',
    'print_result',
    'print_table'
]
