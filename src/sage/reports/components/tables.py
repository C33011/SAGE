"""
Table generators for SAGE reports.

This module provides functions to generate HTML tables
for data quality reports.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd

# Set up logger
logger = logging.getLogger("sage.reports.components.tables")


def generate_details_table(header: List[str], rows: List[List[Any]], class_name: str = None) -> str:
    """
    Generate HTML for a details table.
    
    Args:
        header: List of header column names
        rows: List of row data (list of values)
        class_name: Optional CSS class for the table
        
    Returns:
        HTML string for the table
    """
    class_attr = f' class="{class_name}"' if class_name else ''
    
    html = f'<table{class_attr}>\n<thead>\n<tr>\n'
    
    # Add header
    for col in header:
        html += f'<th>{col}</th>\n'
    
    html += '</tr>\n</thead>\n<tbody>\n'
    
    # Add rows
    for row in rows:
        html += '<tr>\n'
        for cell in row:
            html += f'<td>{cell}</td>\n'
        html += '</tr>\n'
    
    html += '</tbody>\n</table>'
    
    return html


def generate_metric_details_table(metric_name: str, column_data: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate HTML table for metric column details.
    
    Args:
        metric_name: Name of the metric
        column_data: Dictionary mapping column names to column details
        
    Returns:
        HTML string for the table
    """
    if not column_data:
        return ""
    
    # Determine table structure based on metric
    if metric_name.lower() == 'completeness':
        header = ['Column', 'Score', 'Status', 'Details']
        rows = []
        
        for col, data in column_data.items():
            score = data.get('score', data.get('completeness', 0))
            score_str = f"{score:.1%}" if isinstance(score, (int, float)) else str(score)
            status = data.get('status', '')
            message = data.get('message', '')
            
            rows.append([
                col,
                score_str,
                f'<span class="status-{status}">{status}</span>',
                message
            ])
    
    elif metric_name.lower() == 'accuracy':
        header = ['Column', 'Valid', 'Invalid', 'Details']
        rows = []
        
        for col, data in column_data.items():
            valid = data.get('valid', 0)
            invalid = data.get('invalid', 0)
            message = data.get('message', '')
            
            rows.append([col, valid, invalid, message])
    
    elif metric_name.lower() == 'uniqueness':
        header = ['Column', 'Unique %', 'Duplicates', 'Details']
        rows = []
        
        for col, data in column_data.items():
            score = data.get('score', 0)
            score_str = f"{score:.1%}" if isinstance(score, (int, float)) else str(score)
            duplicates = data.get('duplicates', 0)
            message = data.get('message', '')
            
            rows.append([col, score_str, duplicates, message])
    
    else:
        # Generic structure for other metrics
        header = ['Column', 'Score', 'Status', 'Details']
        rows = []
        
        for col, data in column_data.items():
            score = data.get('score', 0)
            score_str = f"{score:.1%}" if isinstance(score, (int, float)) else str(score)
            status = data.get('status', '')
            message = data.get('message', '')
            
            rows.append([
                col,
                score_str,
                f'<span class="status-{status}">{status}</span>',
                message
            ])
    
    return generate_details_table(header, rows)


def generate_dataframe_preview(df: pd.DataFrame, max_rows: int = 10) -> str:
    """
    Generate HTML table for dataframe preview.
    
    Args:
        df: DataFrame to display
        max_rows: Maximum number of rows to show
        
    Returns:
        HTML string for the table
    """
    if df is None or df.empty:
        return "<p>No data available for preview</p>"
    
    # Get subset of dataframe
    preview_df = df.head(max_rows)
    
    # Generate header
    header = list(preview_df.columns)
    
    # Generate rows
    rows = []
    for _, row in preview_df.iterrows():
        # Format the values for display
        formatted_row = []
        for val in row:
            if pd.isna(val):
                formatted_row.append('<em class="missing-value">null</em>')
            elif isinstance(val, (int, float)):
                formatted_row.append(str(val))
            else:
                # Truncate long strings
                val_str = str(val)
                if len(val_str) > 50:
                    formatted_row.append(f"{val_str[:50]}...")
                else:
                    formatted_row.append(val_str)
        rows.append(formatted_row)
    
    # Generate table
    table_html = generate_details_table(header, rows, "data-preview-table")
    
    # Add note if showing partial data
    if len(df) > max_rows:
        table_html += f"<p class='preview-note'>Showing {max_rows} of {len(df)} rows</p>"
    
    return table_html
