"""
SAGE visualization package.

This package provides functionality for creating charts, visualizations, and
formatting data for visual display.
"""

from sage.visualization.chart_generators import (
    generate_bar_chart,
    generate_pie_chart,
    generate_line_chart,
    generate_quality_score_gauge,
    generate_column_quality_heatmap
)

from sage.visualization.data_formatters import (
    prepare_categorical_data,
    aggregate_scores,
    pivot_metric_scores,
    convert_to_chartjs_format
)

# List of functions to expose when using `from sage.visualization import *`
__all__ = [
    # Chart generators
    'generate_bar_chart',
    'generate_pie_chart',
    'generate_line_chart',
    'generate_quality_score_gauge',
    'generate_column_quality_heatmap',
    
    # Data formatters
    'prepare_categorical_data',
    'aggregate_scores',
    'pivot_metric_scores', 
    'convert_to_chartjs_format'
]
