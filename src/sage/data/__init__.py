"""
SAGE data package.

This package provides functionality for working with data sources
and performing data analysis operations.
"""

try:
    from sage.data.profiler import DataProfiler, profile_dataframe, profile_column
    
    __all__ = [
        'DataProfiler',
        'profile_dataframe',
        'profile_column'
    ]
except ImportError as e:
    import logging
    logging.getLogger("sage.data").warning(f"Error importing data profiler: {e}")
    
    # Define placeholder classes if imports fail
    class DataProfiler:
        """Placeholder for unavailable DataProfiler."""
        def __init__(self, *args, **kwargs):
            raise ImportError("DataProfiler is not available")
    
    def profile_dataframe(*args, **kwargs):
        """Placeholder for unavailable function."""
        raise ImportError("profile_dataframe is not available")
        
    def profile_column(*args, **kwargs):
        """Placeholder for unavailable function."""
        raise ImportError("profile_column is not available")
