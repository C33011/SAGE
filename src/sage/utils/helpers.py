"""
General utility functions for SAGE.

This module provides common helper functions used throughout the SAGE library
for file operations, data manipulation, and other shared functionality.
"""

import os
import json
import yaml
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from pathlib import Path
import datetime
import re

# Set up logger
logger = logging.getLogger("sage.utils")


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get metadata information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file metadata (size, type, modified date, etc.)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_stat = os.stat(file_path)
    file_path_obj = Path(file_path)
    
    return {
        "path": file_path,
        "filename": file_path_obj.name,
        "extension": file_path_obj.suffix.lower(),
        "size_bytes": file_stat.st_size,
        "size_human": format_file_size(file_stat.st_size),
        "modified_timestamp": file_stat.st_mtime,
        "modified_date": datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
        "created_timestamp": file_stat.st_ctime,
        "created_date": datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
        "is_excel": file_path_obj.suffix.lower() in ('.xlsx', '.xls', '.xlsm'),
        "is_csv": file_path_obj.suffix.lower() == '.csv',
        "is_db": file_path_obj.suffix.lower() in ('.db', '.sqlite', '.sqlite3'),
    }


def format_file_size(size_bytes: int) -> str:
    """
    Format a file size in bytes to a human-readable string.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Human-readable file size (e.g., "2.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    idx = 0
    
    while size_bytes >= 1024 and idx < len(suffixes) - 1:
        size_bytes /= 1024
        idx += 1
    
    return f"{size_bytes:.2f} {suffixes[idx]}"


def validate_file_exists(file_path: str, expected_extension: Optional[str] = None) -> bool:
    """
    Validate that a file exists and has the expected extension.
    
    Args:
        file_path: Path to the file
        expected_extension: Expected file extension (e.g., '.xlsx')
        
    Returns:
        True if file exists and has the expected extension
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file has the wrong extension
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if expected_extension and not file_path.lower().endswith(expected_extension.lower()):
        raise ValueError(f"File has wrong extension. Expected {expected_extension}")
    
    return True


def normalize_column_names(df: pd.DataFrame, 
                          lowercase: bool = True,
                          replace_spaces: bool = True,
                          replace_char: str = "_") -> pd.DataFrame:
    """
    Normalize column names in a dataframe for consistency.
    
    Args:
        df: Input dataframe
        lowercase: Convert column names to lowercase
        replace_spaces: Replace spaces with another character
        replace_char: Character to replace spaces with
        
    Returns:
        DataFrame with normalized column names
    """
    # Create a copy to avoid modifying the original
    result = df.copy()
    
    # Get current column names
    columns = list(df.columns)
    
    # Create normalized column names
    normalized = []
    for col in columns:
        # Convert to string if not already
        col_str = str(col)
        
        # Apply transformations
        if lowercase:
            col_str = col_str.lower()
        
        if replace_spaces:
            col_str = col_str.replace(" ", replace_char)
        
        # Remove other problematic characters
        col_str = re.sub(r'[^\w' + re.escape(replace_char) + r']', '', col_str)
        
        normalized.append(col_str)
    
    # Rename columns
    result.columns = normalized
    
    return result


def is_empty_value(value: Any) -> bool:
    """
    Check if a value should be considered empty.
    
    Args:
        value: The value to check
        
    Returns:
        True if the value is considered empty
    """
    # Check for None, NaN, etc.
    if value is None or pd.isna(value):
        return True
    
    # Check for empty strings (including whitespace-only)
    if isinstance(value, str) and value.strip() == "":
        return True
    
    # Check for specific "empty" text values
    if isinstance(value, str) and value.lower() in ("n/a", "none", "null", "na", "-", "--"):
        return True
    
    return False


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a decimal value as a percentage string.
    
    Args:
        value: Decimal value (0.0 to 1.0)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def load_config_file(file_path: str) -> Dict[str, Any]:
    """
    Load a configuration file (JSON or YAML).
    
    Args:
        file_path: Path to the configuration file
        
    Returns:
        Configuration as a dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is unsupported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        with open(file_path, 'r') as f:
            if file_extension in ('.json'):
                return json.load(f)
            elif file_extension in ('.yaml', '.yml'):
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_extension}")
    except Exception as e:
        logger.error(f"Failed to load configuration file {file_path}: {str(e)}")
        raise


def safe_divide(numerator: Union[int, float], 
               denominator: Union[int, float], 
               default: Union[int, float] = 0) -> float:
    """
    Safely divide two numbers, returning a default value if the denominator is zero.
    
    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Value to return if denominator is zero
        
    Returns:
        Division result or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def get_data_type_summary(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Get a summary of data types and their statistics for each column.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary mapping column names to type information
    """
    result = {}
    
    for column in df.columns:
        # Get the pandas dtype
        dtype = df[column].dtype
        col_data = df[column]
        
        # Determine the high-level type category
        if pd.api.types.is_numeric_dtype(dtype):
            # Further categorize numeric
            if pd.api.types.is_integer_dtype(dtype) or (
                col_data.dropna().apply(lambda x: float(x).is_integer() if isinstance(x, (int, float)) 
                                         else True).all()):
                type_category = "integer"
            else:
                type_category = "float"
        elif pd.api.types.is_datetime64_dtype(dtype):
            type_category = "datetime"
        elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
            type_category = "string"
        elif pd.api.types.is_bool_dtype(dtype):
            type_category = "boolean"
        elif pd.api.types.is_categorical_dtype(dtype):
            type_category = "categorical"
        else:
            type_category = "other"
        
        # Get statistics appropriate for the type
        stats = {}
        try:
            if type_category in ("integer", "float"):
                stats = {
                    "min": float(col_data.min()) if not pd.isna(col_data.min()) else None,
                    "max": float(col_data.max()) if not pd.isna(col_data.max()) else None,
                    "mean": float(col_data.mean()) if not pd.isna(col_data.mean()) else None,
                    "median": float(col_data.median()) if not pd.isna(col_data.median()) else None,
                    "std": float(col_data.std()) if not pd.isna(col_data.std()) else None,
                }
            elif type_category == "datetime":
                stats = {
                    "min": col_data.min().isoformat() if not pd.isna(col_data.min()) else None,
                    "max": col_data.max().isoformat() if not pd.isna(col_data.max()) else None,
                }
            elif type_category in ("string", "mixed", "categorical"):
                # Get unique values count
                unique_count = col_data.nunique()
                stats = {
                    "unique_count": unique_count,
                    "unique_ratio": safe_divide(unique_count, len(col_data)),
                }
                
                # If there aren't too many unique values, include them
                if unique_count <= 10:
                    stats["unique_values"] = col_data.dropna().unique().tolist()
        except Exception as e:
            logger.warning(f"Error calculating statistics for column '{column}': {str(e)}")
        
        result[column] = {
            "dtype": str(dtype),
            "type_category": type_category,
            "null_count": int(col_data.isna().sum()),
            "null_percentage": float(col_data.isna().mean()),
            "stats": stats
        }
    
    return result


def format_number(value: Union[int, float], 
                 decimals: int = 2, 
                 as_percent: bool = False) -> str:
    """
    Format a number as string with proper formatting.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        as_percent: Whether to format as percentage
        
    Returns:
        Formatted string
    """
    if not isinstance(value, (int, float)):
        return str(value)
    
    if as_percent:
        return f"{value * 100:.{decimals}f}%"
    elif value.is_integer():
        return f"{int(value):,}"
    else:
        return f"{value:,.{decimals}f}"


def truncate_string(text: str, 
                   max_length: int = 100, 
                   suffix: str = "...") -> str:
    """
    Truncate a string if it exceeds maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum allowed length
        suffix: String to append when truncated
        
    Returns:
        Truncated string
    """
    if not isinstance(text, str):
        text = str(text)
        
    if len(text) <= max_length:
        return text
    
    # Ensure we leave room for the suffix
    trunc_length = max_length - len(suffix)
    return text[:trunc_length] + suffix


def detect_encoding(file_path: str) -> str:
    """
    Attempt to detect the encoding of a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Detected encoding or 'utf-8' as fallback
    """
    # This is a simple implementation - for production code you might
    # want to use a more robust library like 'chardet'
    try:
        import chardet
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024)  # Read a sample of the file
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    except ImportError:
        # If chardet is not available, try some common encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(100)  # Try to read a bit of the file
                return encoding
            except UnicodeDecodeError:
                continue
        
        # Fall back to UTF-8
        return 'utf-8'
