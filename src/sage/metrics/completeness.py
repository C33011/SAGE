"""
Completeness metric implementation for SAGE.

This module provides the CompletenessMetric class for measuring
the presence of non-null values in data.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np

from sage.metrics.base_metric import BaseMetric

# Set up logger
logger = logging.getLogger("sage.metrics.completeness")


class CompletenessMetric(BaseMetric):
    """
    Completeness metric for measuring non-null values.
    
    This metric calculates the percentage of non-null values in the data,
    both overall and per column.
    """
    
    def __init__(self, name: str = None, warning_threshold: float = 0.8, failure_threshold: float = 0.6):
        """
        Initialize a completeness metric.
        
        Args:
            name: Optional name for this metric
            warning_threshold: Score threshold below which status becomes 'warning'
            failure_threshold: Score threshold below which status becomes 'failed'
        """
        super().__init__(name)
        
        # Configuration
        self.warning_threshold = warning_threshold
        self.failure_threshold = failure_threshold
        
        logger.debug(f"Initialized completeness metric: {self.name}")
    
    def _get_status(self, score: float) -> str:
        """
        Get status based on score and thresholds.
        
        Args:
            score: Completeness score (0-1)
            
        Returns:
            Status string ('passed', 'warning', or 'failed')
        """
        if score >= self.warning_threshold:
            return 'passed'
        elif score >= self.failure_threshold:
            return 'warning'
        else:
            return 'failed'
    
    def evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate completeness on a dataframe.
        
        Args:
            df: DataFrame to evaluate
            
        Returns:
            Dictionary with evaluation results
        """
        if df is None or df.empty:
            return {
                'score': 0,
                'status': 'failed',
                'message': 'No data to evaluate',
                'columns': {}
            }
        
        # Calculate total cells and missing counts
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        
        # Calculate overall completeness
        if total_cells > 0:
            overall_completeness = (total_cells - missing_cells) / total_cells
        else:
            overall_completeness = 0
        
        # Calculate per-column completeness
        column_results = {}
        
        for column in df.columns:
            col_data = df[column]
            col_size = len(col_data)
            col_missing = col_data.isna().sum()
            
            # Calculate column completeness
            if col_size > 0:
                col_completeness = (col_size - col_missing) / col_size
            else:
                col_completeness = 0
            
            # Determine status based on thresholds
            col_status = self._get_status(col_completeness)
            
            # Create message
            if col_missing == 0:
                col_message = "All values present"
            else:
                col_message = f"Missing {col_missing} of {col_size} values"
            
            # Store result
            column_results[column] = {
                'completeness': col_completeness,
                'status': col_status,
                'message': col_message,
                'missing_count': int(col_missing),
                'total_count': int(col_size)
            }
        
        # Determine overall status based on score
        status = self._get_status(overall_completeness)
        
        # Create summary message
        if missing_cells == 0:
            message = "All values present"
        else:
            message = f"Missing {missing_cells} of {total_cells} values ({overall_completeness:.1%} complete)"
        
        return {
            'score': overall_completeness,
            'status': status,
            'message': message,
            'columns': column_results
        }
    
    def clear(self) -> None:
        """Reset any internal state or configuration."""
        # CompletenessMetric doesn't have configuration to clear
        logger.debug(f"Cleared completeness metric: {self.name}")
