"""
Excel grader implementation for SAGE.

This module provides functionality to assess data quality in Excel files
using configurable metrics and scoring criteria.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
import datetime
import pandas as pd
import os
from pathlib import Path
import time

from sage.graders.base_grader import BaseGrader

# Set up logger
logger = logging.getLogger("sage.graders.excel")


class ExcelGrader(BaseGrader):
    """
    Data quality grader for Excel sources.
    
    Connects to Excel files and applies metrics to assess data quality.
    Supports multiple worksheets and Excel-specific features.
    """
    
    def __init__(self, name: str = None):
        """
        Initialize an Excel grader.
        
        Args:
            name: Human-readable name for this grader
        """
        super().__init__(name)
        
        # Excel-specific properties
        self.excel_path = None        # Path to Excel file
        self.worksheets = {}          # Dictionary of worksheet DataFrames
        self.active_sheet = None      # Currently selected worksheet name
        
        logger.debug(f"Initialized Excel grader: {self.name}")
    
    def connect(self, source: Union[str, pd.DataFrame, Dict[str, pd.DataFrame]]) -> bool:
        """
        Connect to an Excel data source.
        
        Args:
            source: Either:
                   - Path to Excel file
                   - Pandas DataFrame
                   - Dictionary of DataFrames keyed by sheet name
                   
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            ValueError: If source type is not supported
            FileNotFoundError: If Excel file doesn't exist
        """
        try:
            # Reset state
            self.worksheets = {}
            self.active_sheet = None
            self.is_connected = False
            
            if isinstance(source, str):
                # It's a file path
                if not os.path.exists(source):
                    raise FileNotFoundError(f"Excel file not found: {source}")
                
                # Load Excel file into DataFrames
                self.excel_path = source
                logger.info(f"Loading Excel file: {source}")
                
                # Use pandas to read Excel file
                with pd.ExcelFile(source) as xls:
                    for sheet_name in xls.sheet_names:
                        self.worksheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
                
                # Set the first sheet as active if available
                if self.worksheets:
                    self.active_sheet = list(self.worksheets.keys())[0]
                
            elif isinstance(source, pd.DataFrame):
                # It's a single DataFrame
                self.worksheets = {"Sheet1": source}
                self.active_sheet = "Sheet1"
                
            elif isinstance(source, dict) and all(isinstance(v, pd.DataFrame) for v in source.values()):
                # It's a dictionary of DataFrames
                self.worksheets = source
                
                # Set the first sheet as active if available
                if self.worksheets:
                    self.active_sheet = list(self.worksheets.keys())[0]
                    
            else:
                raise ValueError("Source must be an Excel file path, DataFrame, or dictionary of DataFrames")
            
            # Mark connection as successful
            self.source = source
            self.is_connected = True
            
            # Log connection summary
            logger.info(f"Connected to Excel source with {len(self.worksheets)} sheets")
            for sheet, df in self.worksheets.items():
                logger.debug(f"  Sheet '{sheet}': {len(df)} rows, {len(df.columns)} columns")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Excel source: {str(e)}")
            # Re-raise so the caller can handle it
            raise
    
    def get_available_sheets(self) -> List[str]:
        """
        Get list of available worksheets.
        
        Returns:
            List of worksheet names
        """
        if not self.is_connected:
            raise ValueError("Not connected to an Excel source")
        
        return list(self.worksheets.keys())
    
    def set_active_sheet(self, sheet_name: str) -> bool:
        """
        Set the active worksheet for grading operations.
        
        Args:
            sheet_name: Worksheet name to set as active
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If sheet doesn't exist
        """
        if not self.is_connected:
            raise ValueError("Not connected to an Excel source")
        
        if sheet_name not in self.worksheets:
            raise ValueError(f"Worksheet '{sheet_name}' does not exist")
        
        self.active_sheet = sheet_name
        logger.debug(f"Set active sheet to: {sheet_name}")
        return True
    
    def get_column_info(self, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about columns in a worksheet.
        
        Args:
            sheet_name: Worksheet name (uses active sheet if None)
            
        Returns:
            Dictionary with column metadata
        """
        if not self.is_connected:
            raise ValueError("Not connected to an Excel source")
        
        use_sheet = sheet_name or self.active_sheet
        
        if not use_sheet:
            raise ValueError("No active sheet selected")
        
        if use_sheet not in self.worksheets:
            raise ValueError(f"Worksheet '{use_sheet}' does not exist")
        
        # Get the worksheet data
        df = self.worksheets[use_sheet]
        
        # Get basic info about each column
        columns = {}
        for col in df.columns:
            # Get column data
            col_data = df[col]
            
            # Calculate basic stats
            columns[col] = {
                "dtype": str(col_data.dtype),
                "null_count": int(col_data.isna().sum()),
                "unique_count": col_data.nunique(),
                "sample_values": col_data.dropna().sample(min(5, len(col_data.dropna()))).tolist()
            }
        
        return {
            "sheet_name": use_sheet,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": columns
        }
    
    def get_active_data(self) -> pd.DataFrame:
        """
        Get the active worksheet data as a DataFrame.
        
        Returns:
            DataFrame of the active worksheet or None if not connected or no active sheet
        """
        if not self.is_connected or not self.active_sheet:
            return None
            
        return self.worksheets.get(self.active_sheet)
    
    def grade(self, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run metrics against the active worksheet.
        
        Args:
            metrics: Optional list of metric names to run (runs all if None)
            
        Returns:
            Dictionary of results keyed by metric name
            
        Raises:
            ValueError: If no metrics are configured or no worksheet is active
        """
        if not self.active_sheet:
            raise ValueError("No active sheet selected. Call set_active_sheet() first.")
        
        # Get the metrics to run
        metrics_to_run = self._prepare_for_grading(metrics)
        
        if not metrics_to_run:
            logger.warning("No metrics to run - returning empty results")
            return {}
        
        # Get the worksheet data
        df = self.worksheets[self.active_sheet]
        
        # Run each metric and collect results
        results = {}
        start_time = datetime.datetime.now()
        
        for name, metric in metrics_to_run:
            try:
                # Apply the metric to the dataframe
                metric_result = metric.evaluate(df)
                results[name] = metric_result
                logger.debug(f"Metric '{name}' completed with score: {metric_result.get('score', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Error running metric '{name}': {str(e)}")
                # Store the error but don't fail the whole grading process
                results[name] = {
                    "error": str(e),
                    "status": "failed",
                    "score": 0
                }
        
        # Calculate timing information
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Enrich results with metadata
        results_with_meta = {
            "metrics": results,
            "metadata": {
                "excel": {
                    "file_path": self.excel_path,
                    "active_sheet": self.active_sheet,
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns)
                },
                "timing": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration
                }
            }
        }
        
        # Store results
        self._store_results(results)
        
        logger.info(f"Excel grading completed in {duration:.2f} seconds with {len(results)} metrics")
        
        return results_with_meta
