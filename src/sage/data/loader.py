"""
Data loading functionality for SAGE.

This module provides functions for loading data from various file formats
and sources into pandas DataFrames for analysis.
"""

import os
import logging
from typing import Optional, Union, Dict, Any
import pandas as pd

# Set up logger
logger = logging.getLogger("sage.data.loader")

def load_data(file_path: str, 
             sheet_name: Optional[str] = None,
             **kwargs) -> pd.DataFrame:
    """
    Load data from a file into a pandas DataFrame.
    
    Supports various file formats including CSV, Excel, JSON, and parquet.
    
    Args:
        file_path: Path to the data file
        sheet_name: For Excel files, the name of the sheet to load
        **kwargs: Additional arguments to pass to the pandas read functions
        
    Returns:
        Loaded DataFrame
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine file type from extension
    _, ext = os.path.splitext(file_path.lower())
    
    try:
        if ext in ['.xlsx', '.xls', '.xlsm', '.xlsb', '.odf', '.ods', '.odt']:
            # Excel files
            logger.info(f"Loading Excel file: {file_path}")
            if sheet_name:
                logger.info(f"Using sheet: {sheet_name}")
                df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            else:
                # If no sheet specified, read the first sheet
                df = pd.read_excel(file_path, **kwargs)
                
        elif ext == '.csv':
            # CSV files
            logger.info(f"Loading CSV file: {file_path}")
            df = pd.read_csv(file_path, **kwargs)
            
        elif ext == '.json':
            # JSON files
            logger.info(f"Loading JSON file: {file_path}")
            df = pd.read_json(file_path, **kwargs)
            
        elif ext == '.parquet':
            # Parquet files
            logger.info(f"Loading Parquet file: {file_path}")
            df = pd.read_parquet(file_path, **kwargs)
            
        elif ext in ['.pickle', '.pkl']:
            # Pickle files
            logger.info(f"Loading Pickle file: {file_path}")
            df = pd.read_pickle(file_path, **kwargs)
            
        elif ext == '.feather':
            # Feather files
            logger.info(f"Loading Feather file: {file_path}")
            df = pd.read_feather(file_path, **kwargs)
            
        elif ext in ['.h5', '.hdf5']:
            # HDF5 files
            logger.info(f"Loading HDF5 file: {file_path}")
            df = pd.read_hdf(file_path, **kwargs)
            
        elif ext == '.sql':
            # SQL query files
            from sqlalchemy import create_engine
            
            logger.info(f"Reading SQL query from {file_path}")
            with open(file_path, 'r') as f:
                query = f.read()
                
            # Check if connection string is provided in kwargs
            if 'connection_string' not in kwargs:
                raise ValueError("connection_string must be provided for SQL files")
                
            connection_string = kwargs.pop('connection_string')
            engine = create_engine(connection_string)
            
            logger.info("Executing SQL query")
            df = pd.read_sql_query(query, engine, **kwargs)
            
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        logger.info(f"Successfully loaded data with {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {str(e)}")
        raise
