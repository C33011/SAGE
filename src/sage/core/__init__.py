"""
SAGE core package.

This package provides the central analysis and coordination functionality
for data quality assessment.
"""

from sage.core.analyzer import Analyzer

# List of classes to expose when using `from sage.core import *`
__all__ = [
    'Analyzer'
]
