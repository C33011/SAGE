"""
Base grader class that defines the interface for all SAGE graders.

All specific graders (Excel, Database, etc.) inherit from this class
and implement the required abstract methods.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Tuple
import datetime
import uuid
import pandas as pd

# Set up logger
logger = logging.getLogger("sage.graders")


class BaseGrader(ABC):
    """
    Abstract base class for all data graders.
    
    This class defines the common interface and shared functionality
    that all grader implementations must provide, regardless of data source.
    """
    
    def __init__(self, name: str = None):
        """
        Initialize a grader instance.
        
        Args:
            name: Human-readable name for this grader (defaults to class name if None)
        """
        # Generate a default name if none provided
        self.name = name or f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        
        # Properties to track state and results
        self.metrics = {}                  # Stores metric instances by name
        self.results = {}                  # Stores the last run results
        self.source = None                 # Reference to the data source
        self.is_connected = False          # Connection state flag
        self.last_run_time = None          # When grade() was last called
        self.meta = {}                     # Metadata about the grading run
        
        logger.debug(f"Initialized grader: {self.name}")
    
    @abstractmethod
    def connect(self, source: Any) -> bool:
        """
        Connect to the data source to be graded.
        
        Args:
            source: The data source (format depends on the specific grader)
            
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def grade(self, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the grading process using configured metrics.
        
        Args:
            metrics: Optional list of metric names to run (runs all if None)
            
        Returns:
            Dictionary of results keyed by metric name
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
            ValueError: If no metrics are configured or no data source is connected
        """
        pass
    
    def add_metric(self, name: str, metric_instance: Any) -> None:
        """
        Add a metric to this grader.
        
        Args:
            name: Name for this metric
            metric_instance: The metric object to add
            
        Raises:
            ValueError: If a metric with this name already exists
        """
        if name in self.metrics:
            # Would be nice to allow overwriting, but could cause confusion
            # since someone might accidentally add the same metric twice
            raise ValueError(f"A metric named '{name}' already exists in this grader")
        
        self.metrics[name] = metric_instance
        logger.debug(f"Added metric '{name}' to grader '{self.name}'")
    
    def remove_metric(self, name: str) -> None:
        """
        Remove a metric from this grader.
        
        Args:
            name: Name of the metric to remove
            
        Raises:
            KeyError: If no metric with the given name exists
        """
        if name not in self.metrics:
            raise KeyError(f"No metric named '{name}' exists in this grader")
        
        del self.metrics[name]
        logger.debug(f"Removed metric '{name}' from grader '{self.name}'")
    
    def get_available_metrics(self) -> Set[str]:
        """
        Get the names of all metrics configured in this grader.
        
        Returns:
            Set of metric names
        """
        return set(self.metrics.keys())
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the grader state and latest results.
        
        Returns:
            Dictionary with grader metadata and result summary
        """
        summary = {
            "name": self.name,
            "type": self.__class__.__name__,
            "connected": self.is_connected,
            "metrics_configured": len(self.metrics),
            "last_run": self.last_run_time.isoformat() if self.last_run_time else None,
            "has_results": bool(self.results),
        }
        
        # Add high-level result info if available
        if self.results:
            summary["metrics_run"] = len(self.results)
            # This assumes results has a "score" field - implementations will vary
            scores = [r.get("score", 0) for r in self.results.values() if isinstance(r, dict)]
            if scores:
                summary["avg_score"] = sum(scores) / len(scores)
        
        return summary
    
    def _prepare_for_grading(self, metrics: Optional[List[str]] = None) -> List[Tuple[str, Any]]:
        """
        Prepare for grading by validating state and selecting metrics.
        
        Args:
            metrics: List of metric names to use (uses all if None)
            
        Returns:
            List of (name, metric) tuples to run
            
        Raises:
            ValueError: If no metrics are configured or source not connected
        """
        # Make sure we're connected to a data source
        if not self.is_connected or self.source is None:
            raise ValueError("No data source connected. Call connect() first.")
        
        # Make sure we have metrics configured
        if not self.metrics:
            raise ValueError("No metrics configured. Add metrics before grading.")
        
        # Determine which metrics to run
        if metrics is None:
            # Run all configured metrics
            return list(self.metrics.items())
        else:
            # Run only the specified metrics (if they exist)
            metrics_to_run = []
            for name in metrics:
                if name in self.metrics:
                    metrics_to_run.append((name, self.metrics[name]))
                else:
                    logger.warning(f"Metric '{name}' not found in grader '{self.name}'")
            
            if not metrics_to_run:
                raise ValueError("None of the specified metrics are configured in this grader")
                
            return metrics_to_run
    
    def _store_results(self, results: Dict[str, Any]) -> None:
        """
        Store and post-process grading results.
        
        Args:
            results: Results dictionary from a grading run
        """
        self.results = results
        self.last_run_time = datetime.datetime.now()
        
        # Add metadata about this run
        self.meta = {
            "timestamp": self.last_run_time.isoformat(),
            "metrics_run": list(results.keys()),
            "duration_seconds": None,  # Would be calculated from start/end time
        }
        
        logger.info(f"Grader '{self.name}' completed with {len(results)} metrics")
    
    def get_active_data(self) -> pd.DataFrame:
        """
        Get the active data being graded.
        
        Returns:
            DataFrame of the active data or None if not applicable
        """
        # To be implemented by subclasses
        return None
    
    def __str__(self) -> str:
        """String representation of this grader."""
        status = "connected" if self.is_connected else "disconnected"
        return f"{self.__class__.__name__}('{self.name}', {status}, {len(self.metrics)} metrics)"
    
    def __repr__(self) -> str:
        """Detailed string representation of this grader."""
        return f"{self.__class__.__name__}(name='{self.name}', metrics={len(self.metrics)})"
