"""
Data formatting utilities for SAGE visualizations.

This module provides functions to transform and prepare data for visualization,
handling various data formats and preprocessing requirements.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Set
import pandas as pd
import numpy as np
import datetime
from collections import defaultdict, Counter

# Set up logger
logger = logging.getLogger("sage.visualization.formatters")


def format_data_for_charts(data: Any, chart_type: str) -> Dict[str, Any]:
    """
    Format generic data for specific chart types.
    
    Intelligently converts various data formats to the structure
    required by different chart types.
    
    Args:
        data: Data to format (dict, list, DataFrame, etc.)
        chart_type: Type of chart ('bar', 'pie', 'line', etc.)
        
    Returns:
        Formatted data suitable for the specified chart type
    """
    # Convert pandas DataFrame to dict if necessary
    if isinstance(data, pd.DataFrame):
        if chart_type in ['bar', 'pie']:
            # For bar/pie charts, use the first two columns as categories and values
            if len(data.columns) >= 2:
                # Convert first two columns to category-value pairs
                return dict(zip(data.iloc[:, 0].astype(str), data.iloc[:, 1]))
            else:
                # Use value counts of a single column
                return dict(data.iloc[:, 0].value_counts())
                
        elif chart_type == 'line':
            # For line charts, use the first column as x-axis and other columns as series
            result = {}
            x_values = data.iloc[:, 0].tolist()
            
            for col in data.columns[1:]:
                y_values = data[col].tolist()
                result[col] = list(zip(x_values, y_values))
                
            return result
            
        elif chart_type in ['scatter', 'bubble']:
            # For scatter plots, use the first two columns as x,y coordinates
            if len(data.columns) >= 2:
                return {
                    'x': data.iloc[:, 0].tolist(),
                    'y': data.iloc[:, 1].tolist(),
                    'size': data.iloc[:, 2].tolist() if len(data.columns) >= 3 else None
                }
    
    # Handle dictionary data
    elif isinstance(data, dict):
        if chart_type in ['bar', 'pie']:
            # Make sure values are numbers
            return {str(k): float(v) if isinstance(v, (int, float)) else 0 
                   for k, v in data.items()}
                   
        elif chart_type == 'line' and all(isinstance(v, list) for v in data.values()):
            # Check if it's already in the right format for line charts
            return data
    
    # Handle list data
    elif isinstance(data, list):
        if chart_type in ['bar', 'pie']:
            # For lists of strings, count occurrences
            if all(isinstance(x, str) for x in data):
                return dict(Counter(data))
            # For lists of numbers, use indices as categories
            elif all(isinstance(x, (int, float)) for x in data):
                return {str(i): x for i, x in enumerate(data)}
        
        elif chart_type == 'line':
            # For lists of tuples/lists (points), create a single series
            if all(isinstance(x, (tuple, list)) and len(x) == 2 for x in data):
                return {"Series": data}
    
    # If no specific formatting was done, return the original data
    logger.warning(f"No specific formatting applied for {chart_type} chart")
    return data


def prepare_timeseries_data(data: Union[pd.DataFrame, Dict[str, List]], 
                           time_column: Optional[str] = None,
                           value_columns: Optional[List[str]] = None,
                           resample: Optional[str] = None) -> Dict[str, List[Tuple]]:
    """
    Prepare time series data for visualization.
    
    Args:
        data: Time series data (DataFrame or dict)
        time_column: Name of the column containing timestamps
        value_columns: Columns to include as values
        resample: Optional resampling frequency (e.g., 'D' for daily)
        
    Returns:
        Dict mapping series names to lists of (timestamp, value) tuples
    """
    result = {}
    
    # Handle DataFrame input
    if isinstance(data, pd.DataFrame):
        # If time_column not specified, try to use the index if it's datetime
        if time_column is None and isinstance(data.index, pd.DatetimeIndex):
            timestamps = data.index
        # Otherwise, try to find a datetime column
        elif time_column is None:
            # Look for datetime columns
            datetime_cols = [col for col in data.columns 
                            if pd.api.types.is_datetime64_dtype(data[col])]
            if datetime_cols:
                time_column = datetime_cols[0]
                timestamps = data[time_column]
            else:
                # Try to convert a column to datetime
                for col in data.columns:
                    try:
                        timestamps = pd.to_datetime(data[col])
                        time_column = col
                        break
                    except:
                        continue
                else:
                    raise ValueError("No time column found and none specified")
        else:
            # Use the specified time column
            try:
                timestamps = pd.to_datetime(data[time_column])
            except:
                raise ValueError(f"Could not convert '{time_column}' to datetime")
        
        # If value_columns not specified, use all numeric columns except the time column
        if value_columns is None:
            value_columns = [col for col in data.columns 
                            if col != time_column and pd.api.types.is_numeric_dtype(data[col])]
        
        # If no numeric columns found, raise error
        if not value_columns:
            raise ValueError("No numeric value columns found")
        
        # Create temporary DataFrame with timestamps as index
        temp_df = data[value_columns].copy()
        temp_df.index = timestamps
        
        # Apply resampling if specified
        if resample:
            temp_df = temp_df.resample(resample).mean()
        
        # Convert to the desired output format
        for column in value_columns:
            series_data = []
            for ts, value in zip(temp_df.index, temp_df[column]):
                if not pd.isna(value):  # Skip NaN values
                    series_data.append((ts, value))
            result[column] = series_data
    
    # Handle dictionary input
    elif isinstance(data, dict):
        # Expect a dict of series names to lists of (timestamp, value) tuples
        for series_name, series_data in data.items():
            # Convert timestamps to datetime objects if they're not already
            processed_data = []
            for point in series_data:
                if len(point) != 2:
                    continue
                    
                ts, value = point
                
                # Convert timestamp to datetime if it's not already
                if not isinstance(ts, (datetime.datetime, pd.Timestamp)):
                    try:
                        ts = pd.to_datetime(ts)
                    except:
                        logger.warning(f"Could not convert timestamp '{ts}' to datetime")
                        continue
                
                # Add the processed point
                processed_data.append((ts, value))
            
            # Skip empty series
            if not processed_data:
                continue
                
            # Sort by timestamp
            processed_data.sort(key=lambda x: x[0])
            
            # Apply resampling if specified
            if resample:
                # Convert to DataFrame for resampling
                temp_df = pd.DataFrame(processed_data, columns=['timestamp', 'value'])
                temp_df.set_index('timestamp', inplace=True)
                temp_df = temp_df.resample(resample).mean().dropna()
                
                # Convert back to list of tuples
                processed_data = [(ts, value) for ts, value in zip(temp_df.index, temp_df['value'])]
            
            result[series_name] = processed_data
    
    return result


def prepare_categorical_data(data: Union[pd.DataFrame, Dict, List], 
                            category_column: Optional[str] = None,
                            value_column: Optional[str] = None,
                            top_n: Optional[int] = None,
                            sort_by: Optional[str] = None) -> Dict[str, float]:
    """
    Prepare categorical data for visualization in bar or pie charts.
    
    Args:
        data: Categorical data (DataFrame, dict, or list)
        category_column: Name of the column containing categories
        value_column: Name of the column containing values
        top_n: Optional limit to the top N categories
        sort_by: How to sort the data ('value', 'category', or None)
        
    Returns:
        Dict mapping categories to values
    """
    result = {}
    
    # Handle DataFrame input
    if isinstance(data, pd.DataFrame):
        # If columns not specified, try to use the first two columns
        if category_column is None:
            category_column = data.columns[0]
        
        if value_column is None:
            # If there's a second column, use it as values
            if len(data.columns) > 1:
                value_column = data.columns[1]
            # Otherwise, count occurrences of categories
            else:
                counts = data[category_column].value_counts()
                result = counts.to_dict()
        else:
            # Group by category and aggregate values
            grouped = data.groupby(category_column)[value_column].sum()
            result = grouped.to_dict()
    
    # Handle dictionary input
    elif isinstance(data, dict):
        # Dict already maps categories to values
        result = data
    
    # Handle list input
    elif isinstance(data, list):
        # For lists of strings, count occurrences
        if all(isinstance(x, str) for x in data):
            result = dict(Counter(data))
        # For lists of dicts, group by category
        elif all(isinstance(x, dict) for x in data):
            if category_column is None or value_column is None:
                raise ValueError("category_column and value_column must be specified for list of dicts")
                
            grouped = defaultdict(float)
            for item in data:
                if category_column in item and value_column in item:
                    grouped[item[category_column]] += item[value_column]
                    
            result = dict(grouped)
    
    # Apply top_n limit if specified
    if top_n and len(result) > top_n:
        sorted_items = sorted(result.items(), key=lambda x: x[1], reverse=True)
        top_items = sorted_items[:top_n]
        other_sum = sum(v for _, v in sorted_items[top_n:])
        
        result = dict(top_items)
        if other_sum > 0:
            result["Other"] = other_sum
    
    # Apply sorting if specified
    if sort_by == 'value':
        result = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))
    elif sort_by == 'category':
        result = dict(sorted(result.items(), key=lambda x: x[0]))
    
    return result


def aggregate_scores(scores: Dict[str, Dict[str, float]],
                    aggregation: str = 'mean') -> Dict[str, float]:
    """
    Aggregate nested score dictionaries for visualization.
    
    Useful for aggregating scores across metrics or columns.
    
    Args:
        scores: Nested dictionary of scores
        aggregation: Aggregation method ('mean', 'min', 'max', 'sum')
        
    Returns:
        Dictionary of aggregated scores
    """
    result = {}
    
    for key, values in scores.items():
        # Skip non-dict values
        if not isinstance(values, dict):
            continue
            
        # Extract numeric values
        numeric_values = [v for v in values.values() if isinstance(v, (int, float))]
        
        if not numeric_values:
            continue
            
        # Apply aggregation
        if aggregation == 'mean':
            result[key] = sum(numeric_values) / len(numeric_values)
        elif aggregation == 'min':
            result[key] = min(numeric_values)
        elif aggregation == 'max':
            result[key] = max(numeric_values)
        elif aggregation == 'sum':
            result[key] = sum(numeric_values)
        else:
            logger.warning(f"Unknown aggregation method: {aggregation}")
            result[key] = sum(numeric_values) / len(numeric_values)  # Default to mean
    
    return result


def pivot_metric_scores(results: Dict[str, Dict[str, Any]],
                       metric_key: str = 'metrics',
                       score_key: str = 'score') -> Dict[str, Dict[str, float]]:
    """
    Pivot metric scores to create a matrix suitable for heatmaps.
    
    Takes SAGE grading results and creates a column-to-metric score matrix.
    
    Args:
        results: SAGE grading results
        metric_key: Key for accessing metrics in the results
        score_key: Key for accessing scores in each metric
        
    Returns:
        Dictionary mapping columns to metric scores
    """
    # Extract column names and metrics
    columns = []
    metrics = set()
    
    # First pass: collect column names and metrics
    for column_name, column_data in results.items():
        columns.append(column_name)
        
        if metric_key in column_data:
            for metric_name in column_data[metric_key].keys():
                metrics.add(metric_name)
    
    # Initialize result dictionary
    result = {}
    
    # Second pass: extract scores
    for column_name, column_data in results.items():
        column_scores = {}
        
        if metric_key in column_data:
            for metric_name, metric_data in column_data[metric_key].items():
                if score_key in metric_data:
                    column_scores[metric_name] = metric_data[score_key]
        
        result[column_name] = column_scores
    
    return result


def convert_to_chartjs_format(data: Any, chart_type: str) -> Dict[str, Any]:
    """
    Convert data to Chart.js format for interactive charts.
    
    Args:
        data: Data to convert
        chart_type: Chart.js chart type
        
    Returns:
        Data formatted for Chart.js
    """
    if chart_type in ['bar', 'horizontalBar', 'pie', 'doughnut']:
        # For categorical charts
        if isinstance(data, dict):
            return {
                "labels": list(data.keys()),
                "datasets": [{
                    "data": list(data.values()),
                    "backgroundColor": [
                        "#4477AA", "#66CCEE", "#228833", "#CCBB44", "#EE6677", "#AA3377",
                        "#BBBBBB", "#77AADD", "#99DDFF", "#44BB99", "#DDDD77", "#FF9977",
                        "#DDAACC", "#DDDDDD"
                    ][:len(data)]
                }]
            }
    
    elif chart_type == 'line':
        # For time series or sequential data
        datasets = []
        
        if isinstance(data, dict):
            # Each key is a series
            colors = [
                "#4477AA", "#66CCEE", "#228833", "#CCBB44", "#EE6677", "#AA3377",
                "#BBBBBB", "#77AADD", "#99DDFF", "#44BB99", "#DDDD77", "#FF9977"
            ]
            
            for i, (series_name, points) in enumerate(data.items()):
                color = colors[i % len(colors)]
                
                # Extract x and y values
                x_values = [p[0] for p in points]
                y_values = [p[1] for p in points]
                
                datasets.append({
                    "label": series_name,
                    "data": y_values,
                    "borderColor": color,
                    "backgroundColor": f"{color}33",  # Add transparency
                    "fill": False
                })
                
            # Special case for time series
            is_timeseries = False
            if data and all(isinstance(points[0][0], (datetime.datetime, pd.Timestamp)) 
                         for points in data.values() if points):
                is_timeseries = True
                x_values = sorted(set(p[0] for series in data.values() for p in series))
                x_values = [x.isoformat() for x in x_values]
            else:
                # For non-time series, use numbers or strings
                all_x_values = []
                for series in data.values():
                    all_x_values.extend(p[0] for p in series)
                x_values = sorted(set(all_x_values))
            
            return {
                "labels": x_values,
                "datasets": datasets,
                "options": {
                    "scales": {
                        "x": {
                            "type": "time" if is_timeseries else "category",
                            "time": {
                                "unit": "day"
                            } if is_timeseries else {}
                        }
                    }
                }
            }
    
    elif chart_type == 'scatter':
        if isinstance(data, dict) and 'x' in data and 'y' in data:
            return {
                "datasets": [{
                    "label": "Scatter Data",
                    "data": [{"x": x, "y": y} for x, y in zip(data['x'], data['y'])],
                    "backgroundColor": "#4477AA"
                }]
            }
    
    # Fall back to returning the original data
    logger.warning(f"No specific Chart.js formatting applied for {chart_type} chart")
    return data


def generate_summary_stats(data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Generate summary statistics for data visualization.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        Dictionary of summary statistics
    """
    result = {
        "overall": {
            "row_count": len(data),
            "column_count": len(data.columns)
        },
        "columns": {}
    }
    
    # Calculate overall completeness
    na_counts = data.isna().sum()
    total_cells = len(data) * len(data.columns)
    na_cells = na_counts.sum()
    result["overall"]["completeness"] = round(1 - (na_cells / total_cells), 4) if total_cells > 0 else 0
    
    # Process each column
    for column in data.columns:
        col_data = data[column]
        dtype = col_data.dtype
        column_stats = {
            "dtype": str(dtype),
            "na_count": int(na_counts[column]),
            "completeness": round(1 - (na_counts[column] / len(data)), 4) if len(data) > 0 else 0
        }
        
        # Add type-specific statistics
        if pd.api.types.is_numeric_dtype(dtype):
            non_null = col_data.dropna()
            if len(non_null) > 0:
                column_stats.update({
                    "min": float(non_null.min()),
                    "max": float(non_null.max()),
                    "mean": float(non_null.mean()),
                    "median": float(non_null.median()),
                    "std": float(non_null.std())
                })
                
                # Calculate quartiles
                column_stats["quartiles"] = [
                    float(non_null.quantile(0.25)),
                    float(non_null.quantile(0.5)),
                    float(non_null.quantile(0.75))
                ]
                
                # Calculate histogram data
                hist, bins = np.histogram(non_null, bins=10)
                column_stats["histogram"] = {
                    "counts": hist.tolist(),
                    "bins": bins.tolist()
                }
        
        elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
            non_null = col_data.dropna()
            if len(non_null) > 0:
                # Count unique values
                value_counts = non_null.value_counts()
                column_stats["unique_count"] = len(value_counts)
                column_stats["uniqueness_ratio"] = round(len(value_counts) / len(non_null), 4)
                
                # Include top N most common values
                top_values = value_counts.head(10).to_dict()
                column_stats["top_values"] = {str(k): int(v) for k, v in top_values.items()}
                
                # String length statistics
                str_lengths = non_null.astype(str).str.len()
                column_stats["avg_length"] = float(str_lengths.mean())
                column_stats["max_length"] = int(str_lengths.max())
        
        elif pd.api.types.is_datetime64_dtype(dtype):
            non_null = col_data.dropna()
            if len(non_null) > 0:
                column_stats.update({
                    "min": non_null.min().isoformat(),
                    "max": non_null.max().isoformat(),
                    "range_days": (non_null.max() - non_null.min()).total_seconds() / (60 * 60 * 24)
                })
        
        result["columns"][column] = column_stats
    
    return result
