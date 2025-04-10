"""
SAGE: Spreadsheet Analysis Grading Engine.

A comprehensive toolkit for assessing and grading data quality
in spreadsheets, databases, and other data sources.
"""

# Import version information
from sage.version import __version__, __author__, VERSION_INFO

# Import core components that should be available directly from sage package
try:
    from sage.core import Analyzer
except ImportError:
    # If Analyzer doesn't exist yet, don't try to import it
    pass

# Import help functionality
from sage.cli.help import show_help as help

# Define the version - imported from version.py
def get_version():
    """Return the current version of SAGE."""
    return __version__
