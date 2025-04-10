"""
Timeliness metric implementation for SAGE.

This module provides the TimelinessMetric class for measuring
the freshness and age-related aspects of data.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
import datetime

from sage.metrics.base_metric import BaseMetric

# Set up logger
logger = logging.getLogger("sage.metrics.timeliness")


class TimelinessMetric(BaseMetric):
    """
    Timeliness metric for measuring data freshness and age.
    
    This metric evaluates whether data is appropriately current
    based on specified age and freshness criteria.
    """
    
    def __init__(self, name: str = None, warning_threshold: float = 0.9, 
                 failure_threshold: float = 0.7, reference_date: Optional[datetime.date] = None):
        """
        Initialize a timeliness metric.
        
        Args:
            name: Optional name for this metric
            warning_threshold: Score threshold below which status becomes 'warning'
            failure_threshold: Score threshold below which status becomes 'failed'
            reference_date: Date to use as the 'current' date (uses today if None)
        """
        super().__init__(name)
        
        # Configuration
        self.warning_threshold = warning_threshold
        self.failure_threshold = failure_threshold
        self.reference_date = reference_date or datetime.datetime.now().date()
        
        # Store checks
        self.age_checks = {}
        self.freshness_checks = {}
        
        logger.debug(f"Initialized timeliness metric: {self.name} with reference date {self.reference_date}")
    
    def add_age_check(self, column: str, max_age: int, warning_threshold: Optional[int] = None) -> None:
        """
        Add an age check for a date column.
        
        Args:
            column: Name of the date column to check
            max_age: Maximum allowed age in days
            warning_threshold: Age in days that triggers a warning (defaults to max_age/2)
            
        Raises:
            ValueError: If max_age is not positive
        """
        if max_age <= 0:
            raise ValueError("max_age must be a positive integer")
        
        if warning_threshold is None:
            warning_threshold = max_age // 2
        
        self.age_checks[column] = {
            'max_age': max_age,
            'warning_threshold': warning_threshold
        }
        
        logger.debug(f"Added age check for '{column}': max {max_age} days, warning at {warning_threshold} days")
    
    def add_freshness_check(self, column: str, max_age: int, warning_threshold: Optional[int] = None) -> None:
        """
        Add a freshness check for a date/timestamp column.
        
        Args:
            column: Name of the date column to check
            max_age: Maximum allowed age in days
            warning_threshold: Age in days that triggers a warning (defaults to max_age/2)
            
        Raises:
            ValueError: If max_age is not positive
        """
        if max_age <= 0:
            raise ValueError("max_age must be a positive integer")
        
        if warning_threshold is None:
            warning_threshold = max_age // 2
        
        self.freshness_checks[column] = {
            'max_age': max_age,
            'warning_threshold': warning_threshold
        }
        
        logger.debug(f"Added freshness check for '{column}': max {max_age} days, warning at {warning_threshold} days")
    
    def _evaluate_age_check(self, df: pd.DataFrame, column: str, check: Dict[str, int]) -> Dict[str, Any]:
        """
        Evaluate an age check on the dataframe.
        
        Args:
            df: DataFrame to evaluate
            column: Column name to check
            check: Dictionary with check parameters
            
        Returns:
            Dictionary with check results
        """
        if column not in df.columns:
            return {
                'timely': 0,
                'untimely': 0,
                'timeliness_score': 0.0,
                'message': f"Column '{column}' not found in data"
            }
        
        # Get column data, excluding NaN values
        col_data = df[column].dropna()
        
        # Skip if no data after dropping NAs
        if len(col_data) == 0:
            return {
                'timely': 0,
                'untimely': 0,
                'timeliness_score': 1.0,
                'message': f"No non-null values in column '{column}'"
            }
        
        # Check if column is date/datetime type or convert
        try:
            if not pd.api.types.is_datetime64_dtype(col_data):
                # Try to convert to datetime
                col_data = pd.to_datetime(col_data)
        except Exception as e:
            return {
                'timely': 0,
                'untimely': len(col_data),
                'timeliness_score': 0.0,
                'message': f"Could not convert '{column}' to datetime: {str(e)}"
            }
        
        # Extract date component if datetime
        if pd.api.types.is_datetime64_dtype(col_data):
            date_data = col_data.dt.date
        else:
            date_data = col_data
        
        # Calculate age in days
        ref_date = pd.Timestamp(self.reference_date).date()
        
        try:
            # Convert to numpy array of days
            days_diff = np.array([(ref_date - date).days for date in date_data])
        except Exception as e:
            return {
                'timely': 0,
                'untimely': len(col_data),
                'timeliness_score': 0.0,
                'message': f"Error calculating age: {str(e)}"
            }
        
        # Apply age check
        max_age = check['max_age']
        warning_threshold = check.get('warning_threshold', max_age // 2)
        
        # Count results
        timely_count = (days_diff <= max_age).sum()
        untimely_count = len(days_diff) - timely_count
        
        # Calculate timeliness score
        timeliness_score = timely_count / len(days_diff) if len(days_diff) > 0 else 1.0
        
        # Determine status
        if timeliness_score >= self.warning_threshold:
            status = 'passed'
        elif timeliness_score >= self.failure_threshold:
            status = 'warning'
        else:
            status = 'failed'
        
        # Create message
        message = f"Age check: {untimely_count} of {len(days_diff)} values exceed max age of {max_age} days"
        
        return {
            'timely': int(timely_count),
            'untimely': int(untimely_count),
            'timeliness_score': float(timeliness_score),
            'max_age': max_age,
            'warning_threshold': warning_threshold,
            'status': status,
            'message': message,
            'check_type': 'age'
        }
    
    def _evaluate_freshness_check(self, df: pd.DataFrame, column: str, check: Dict[str, int]) -> Dict[str, Any]:
        """
        Evaluate a freshness check on the dataframe.
        
        Args:
            df: DataFrame to evaluate
            column: Column name to check
            check: Dictionary with check parameters
            
        Returns:
            Dictionary with check results
        """
        # Freshness checks are essentially the same as age checks in this implementation
        # But conceptually they can be different (e.g., age is about creation, freshness about updates)
        result = self._evaluate_age_check(df, column, check)
        
        if 'check_type' in result:
            result['check_type'] = 'freshness'
        
        if 'message' in result and 'Age check' in result['message']:
            result['message'] = result['message'].replace('Age check', 'Freshness check')
        
        return result
    
    def evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate timeliness on a dataframe.
        
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
                'details': {}
            }
        
        if not self.age_checks and not self.freshness_checks:
            return {
                'score': 1.0,
                'status': 'passed',
                'message': 'No timeliness checks configured',
                'details': {}
            }
        
        # Evaluate each check
        details = {}
        
        for column, check in self.age_checks.items():
            details[column] = self._evaluate_age_check(df, column, check)
        
        for column, check in self.freshness_checks.items():
            if column in details:
                # Merge with existing results if both age and freshness are checked
                freshness_result = self._evaluate_freshness_check(df, column, check)
                
                # Use the stricter check for the combined result
                existing_score = details[column].get('timeliness_score', 1.0)
                freshness_score = freshness_result.get('timeliness_score', 1.0)
                
                if freshness_score < existing_score:
                    details[column] = freshness_result
            else:
                details[column] = self._evaluate_freshness_check(df, column, check)
        
        # Calculate overall score
        if details:
            # Average the timeliness scores
            scores = [d.get('timeliness_score', 0) for d in details.values()]
            overall_score = sum(scores) / len(scores)
        else:
            overall_score = 1.0
        
        # Determine status based on score
        if overall_score >= self.warning_threshold:
            status = 'passed'
        elif overall_score >= self.failure_threshold:
            status = 'warning'
        else:
            status = 'failed'
        
        # Create summary message
        if not details:
            message = "No timeliness checks evaluated"
        else:
            total_untimely = sum(d.get('untimely', 0) for d in details.values())
            total_checked = sum(d.get('timely', 0) + d.get('untimely', 0) for d in details.values())
            
            if total_checked > 0:
                message = f"{total_untimely} of {total_checked} timeliness checks failed ({overall_score:.1%} timely)"
            else:
                message = "No applicable data for timeliness checks"
        
        return {
            'score': overall_score,
            'status': status,
            'message': message,
            'details': details
        }
    
    def clear(self) -> None:
        """Clear all configured checks."""
        self.age_checks = {}
        self.freshness_checks = {}
        logger.debug(f"Cleared all checks from timeliness metric: {self.name}")
