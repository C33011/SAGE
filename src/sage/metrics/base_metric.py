"""
Base metric implementation for SAGE.

This module provides the foundation for all metrics used in SAGE data quality assessments.
It defines the BaseMetric class with common functionality and interfaces.
"""

import logging
from typing import Dict, Any
import pandas as pd

# Set up logger
logger = logging.getLogger("sage.metrics.base")


class BaseMetric:
    """
    Base class for all SAGE metrics.
    
    This abstract class defines the common interface and functionality
    that all metrics should implement.
    """
    
    def __init__(self, name: str = None):
        """
        Initialize a base metric.
        
        Args:
            name: Name of the metric (default: class name)
        """
        self.name = name or self.__class__.__name__.lower().replace('metric', '')
        logger.debug(f"Initialized base metric: {self.name}")
    
    def evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate the metric on a dataframe.
        
        This is the main method that should be implemented by all metrics.
        
        Args:
            df: DataFrame to evaluate
            
        Returns:
            Dictionary with evaluation results including at least:
            - score: Float between 0 and 1
            - status: "passed", "warning", "failed", or "skipped"
            - message: Human-readable description of the results
            
        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement evaluate()")
    
    def clear(self) -> None:
        """
        Clear any configured settings or rules.
        
        This method should reset the metric to its initial state.
        """
        pass  # Optional to implement in subclasses
    
    def __str__(self) -> str:
        """Return string representation of the metric."""
        return f"{self.__class__.__name__}(name='{self.name}')"
