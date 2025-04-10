"""
SAGE metrics package.

This package contains implementations of various data quality metrics
that can be used to evaluate and score datasets.
"""

try:
    from sage.metrics.accuracy import AccuracyMetric
    from sage.metrics.completeness import CompletenessMetric
    from sage.metrics.consistency import ConsistencyMetric
    from sage.metrics.timeliness import TimelinessMetric
    
    __all__ = [
        'AccuracyMetric',
        'CompletenessMetric',
        'ConsistencyMetric',
        'TimelinessMetric'
    ]
except ImportError as e:
    import logging
    logging.getLogger("sage.metrics").warning(f"Error importing metric classes: {e}")
    
    # Define placeholder classes if imports fail
    # This allows the package to be imported even if some modules are missing
    class MetricNotAvailable:
        """Placeholder for unavailable metrics."""
        def __init__(self, *args, **kwargs):
            raise ImportError(f"This metric is not available: {self.__class__.__name__}")
        
        def evaluate(self, df):
            raise ImportError(f"This metric is not available: {self.__class__.__name__}")
    
    # Create placeholder classes
    class AccuracyMetric(MetricNotAvailable): pass
    class CompletenessMetric(MetricNotAvailable): pass
    class ConsistencyMetric(MetricNotAvailable): pass
    class TimelinessMetric(MetricNotAvailable): pass
