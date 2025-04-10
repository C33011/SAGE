"""
Data profiling functionality for SAGE.

This module provides functions to analyze and profile data,
generating statistics and visualizations to help understand data quality.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import io
import base64

# Set up logger
logger = logging.getLogger("sage.data.profiler")

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    HAS_MATPLOTLIB = True
except ImportError:
    logger.warning("Matplotlib not available - visualization will be disabled")
    HAS_MATPLOTLIB = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    logger.warning("Plotly not available - interactive visualization will be disabled")
    HAS_PLOTLY = False


class DataProfiler:
    """
    Class for profiling data and generating statistics/visualizations.
    """
    
    def __init__(self, data: pd.DataFrame = None):
        """
        Initialize the data profiler.
        
        Args:
            data: DataFrame to profile (can also be set later)
        """
        self.data = data
        self.profiles = {}
        self.overall_stats = {}
        
        if data is not None:
            self.profile_data()
    
    def set_data(self, data: pd.DataFrame) -> None:
        """
        Set the data to profile.
        
        Args:
            data: DataFrame to profile
        """
        self.data = data
        self.profile_data()
    
    def profile_data(self) -> Dict[str, Any]:
        """
        Profile the data and calculate overall statistics.
        
        Returns:
            Dictionary with overall statistics
        """
        if self.data is None or self.data.empty:
            logger.warning("No data to profile")
            return {}
        
        logger.info(f"Profiling DataFrame with {len(self.data)} rows and {len(self.data.columns)} columns")
        
        # Calculate overall statistics
        self.overall_stats = {
            'row_count': len(self.data),
            'column_count': len(self.data.columns),
            'memory_usage': self.data.memory_usage(deep=True).sum(),
            'data_types': self.data.dtypes.value_counts().to_dict(),
            'missing_cells': self.data.isna().sum().sum(),
            'missing_percent': float(self.data.isna().sum().sum() / (len(self.data) * len(self.data.columns))),
            'duplicate_rows': self.data.duplicated().sum(),
            'duplicate_percent': float(self.data.duplicated().sum() / len(self.data) if len(self.data) > 0 else 0),
            'column_names': list(self.data.columns)
        }
        
        # Profile each column
        self.profiles = {}
        for col in self.data.columns:
            self.profiles[col] = self._profile_column(col)
        
        # Add visualizations for overall statistics
        if HAS_MATPLOTLIB:
            self._add_overall_visualizations()
        
        return self.overall_stats
    
    def _profile_column(self, column: str) -> Dict[str, Any]:
        """
        Generate statistics for a single column.
        
        Args:
            column: Column name to profile
            
        Returns:
            Dictionary with column statistics
        """
        if column not in self.data.columns:
            return {}
        
        col_data = self.data[column]
        is_numeric = pd.api.types.is_numeric_dtype(col_data) and not pd.api.types.is_bool_dtype(col_data)
        is_categorical = pd.api.types.is_categorical_dtype(col_data) or len(col_data.dropna().unique()) < min(20, len(col_data.dropna()) / 10)
        is_boolean = pd.api.types.is_bool_dtype(col_data)
        
        # Base statistics for all types
        profile = {
            'dtype': str(col_data.dtype),
            'count': len(col_data),
            'missing_count': col_data.isna().sum(),
            'missing_percent': float(col_data.isna().sum() / len(col_data) if len(col_data) > 0 else 0),
            'unique_count': col_data.nunique(),
            'unique_percent': float(col_data.nunique() / len(col_data.dropna()) if len(col_data.dropna()) > 0 else 0),
            'is_numeric': is_numeric,
            'is_categorical': is_categorical,
            'is_boolean': is_boolean,
            'memory_usage': col_data.memory_usage(deep=True),
            'samples': col_data.dropna().sample(min(5, len(col_data.dropna()))).tolist() if not col_data.empty else []
        }
        
        # Add numeric statistics if applicable
        if is_numeric:
            # Only try to calculate quantiles and other numeric stats for non-boolean numeric data
            profile.update({
                'min': float(col_data.min()) if not col_data.dropna().empty else None,
                'max': float(col_data.max()) if not col_data.dropna().empty else None,
                'mean': float(col_data.mean()) if not col_data.dropna().empty else None,
                'median': float(col_data.median()) if not col_data.dropna().empty else None,
                'std': float(col_data.std()) if not col_data.dropna().empty else None,
                'quantile_25': float(col_data.quantile(0.25)) if not col_data.dropna().empty else None,
                'quantile_75': float(col_data.quantile(0.75)) if not col_data.dropna().empty else None,
                'skewness': float(col_data.skew()) if len(col_data.dropna()) > 2 else None,
                'kurtosis': float(col_data.kurtosis()) if len(col_data.dropna()) > 2 else None,
                'zero_count': (col_data == 0).sum(),
                'negative_count': (col_data < 0).sum() if not col_data.dropna().empty else 0
            })
        # Add boolean statistics
        elif is_boolean:
            true_count = col_data.sum()
            false_count = (~col_data).sum()
            profile.update({
                'true_count': int(true_count),
                'false_count': int(false_count),
                'true_percent': float(true_count / len(col_data.dropna()) if len(col_data.dropna()) > 0 else 0),
                'most_common': 'True' if true_count >= false_count else 'False'
            })
        
        # Add categorical statistics if applicable
        if is_categorical or col_data.dtype == 'object':
            # Get value counts for top categories
            value_counts = col_data.value_counts().head(10).to_dict()
            top_1_percent = col_data.value_counts(normalize=True).head(1).to_dict()
            
            profile.update({
                'top_values': value_counts,
                'top_percent': top_1_percent,
                'category_count': len(col_data.dropna().unique())
            })
        
        # Add datetime statistics if applicable
        if pd.api.types.is_datetime64_dtype(col_data):
            profile.update({
                'min_date': col_data.min().isoformat() if not col_data.dropna().empty else None,
                'max_date': col_data.max().isoformat() if not col_data.dropna().empty else None,
                'date_range_days': (col_data.max() - col_data.min()).days if not col_data.dropna().empty else None
            })
        
        # Add visualizations if matplotlib is available
        if HAS_MATPLOTLIB:
            profile.update(self._add_column_visualizations(column))
        
        return profile
    
    def _add_column_visualizations(self, column: str) -> Dict[str, str]:
        """
        Generate visualizations for a column and return as base64 encoded images.
        
        Args:
            column: Column name to visualize
            
        Returns:
            Dictionary with visualization keys and base64 encoded image data
        """
        visualizations = {}
        col_data = self.data[column]
        
        # Skip empty columns
        if col_data.dropna().empty:
            return visualizations
        
        try:
            # Distribution visualization
            if pd.api.types.is_numeric_dtype(col_data):
                # Histogram for numeric data
                plt.figure(figsize=(6, 4))
                plt.hist(col_data.dropna(), bins=min(30, len(col_data.dropna().unique())), alpha=0.7, color='#4285f4')
                plt.title(f'Distribution of {column}')
                plt.xlabel(column)
                plt.ylabel('Frequency')
                plt.grid(axis='y', alpha=0.3)
                plt.tight_layout()
                
                # Convert plot to base64 image
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                visualizations['distribution'] = base64.b64encode(buf.read()).decode('utf-8')
                
                # Boxplot
                plt.figure(figsize=(6, 2))
                plt.boxplot(col_data.dropna(), vert=False, widths=0.7)
                plt.title(f'Boxplot of {column}')
                plt.xlabel(column)
                plt.tight_layout()
                
                # Convert plot to base64 image
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                visualizations['boxplot'] = base64.b64encode(buf.read()).decode('utf-8')
                
            elif col_data.nunique() < 50:
                # Bar chart for categorical data
                value_counts = col_data.value_counts().head(15)
                
                plt.figure(figsize=(6, 4))
                bars = plt.bar(value_counts.index.astype(str), value_counts.values, color='#4285f4')
                plt.title(f'Value Counts for {column}')
                plt.xlabel(column)
                plt.ylabel('Count')
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', alpha=0.3)
                
                # Add data labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    plt.text(
                        bar.get_x() + bar.get_width()/2.,
                        height + 0.1,
                        str(int(height)),
                        ha='center',
                        va='bottom',
                        rotation=0
                    )
                
                plt.tight_layout()
                
                # Convert plot to base64 image
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                visualizations['distribution'] = base64.b64encode(buf.read()).decode('utf-8')
        
        except Exception as e:
            logger.warning(f"Error creating visualization for column {column}: {e}")
        
        return visualizations
    
    def _add_overall_visualizations(self) -> None:
        """
        Add visualizations for overall statistics to the overall_stats dictionary.
        """
        try:
            # Missing data visualization
            missing_by_column = self.data.isna().sum().sort_values(ascending=False)
            missing_columns = missing_by_column[missing_by_column > 0]
            
            if not missing_columns.empty:
                plt.figure(figsize=(10, 6))
                bars = plt.bar(missing_columns.index.astype(str), missing_columns.values, color='#f4b400')
                plt.title('Missing Values by Column')
                plt.xlabel('Column')
                plt.ylabel('Count of Missing Values')
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', alpha=0.3)
                
                # Add data labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    plt.text(
                        bar.get_x() + bar.get_width()/2.,
                        height + 0.1,
                        str(int(height)),
                        ha='center',
                        va='bottom',
                        rotation=0
                    )
                
                plt.tight_layout()
                
                # Convert plot to base64 image
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                self.overall_stats['missing_visualization'] = base64.b64encode(buf.read()).decode('utf-8')
            
            # Data type visualization
            dtype_counts = self.data.dtypes.astype(str).value_counts()
            
            plt.figure(figsize=(6, 6))
            plt.pie(
                dtype_counts.values,
                labels=[str(x) for x in dtype_counts.index],
                autopct='%1.1f%%',
                startangle=90,
                colors=plt.cm.tab10.colors[:len(dtype_counts)]
            )
            plt.axis('equal')
            plt.title('Column Data Types')
            plt.tight_layout()
            
            # Convert plot to base64 image
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            self.overall_stats['dtype_visualization'] = base64.b64encode(buf.read()).decode('utf-8')
            
        except Exception as e:
            logger.warning(f"Error creating overall visualizations: {e}")
    
    def get_column_profile(self, column: str) -> Dict[str, Any]:
        """
        Get the profile for a specific column.
        
        Args:
            column: Column name
            
        Returns:
            Dictionary with column profile, empty dict if column not found
        """
        return self.profiles.get(column, {})
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """
        Get the overall statistics for the data.
        
        Returns:
            Dictionary with overall statistics
        """
        return self.overall_stats
    
    def generate_profile_report(self) -> Dict[str, Any]:
        """
        Generate a complete profile report with overall stats and column profiles.
        
        Returns:
            Dictionary with profile report data
        """
        return {
            'overall_stats': self.overall_stats,
            'column_profiles': self.profiles
        }


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to profile a DataFrame.
    
    Args:
        df: DataFrame to profile
        
    Returns:
        Dictionary with profile report data
    """
    profiler = DataProfiler(df)
    return profiler.generate_profile_report()


def profile_column(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Convenience function to profile a single column from a DataFrame.
    
    Args:
        df: DataFrame containing the column
        column: Name of the column to profile
        
    Returns:
        Dictionary with column profile data
        
    Raises:
        ValueError: If column name is not in the DataFrame
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    profiler = DataProfiler(df)
    profile = profiler.get_column_profile(column)
    
    if not profile:
        # If no profile was generated, create a minimal one
        profile = {
            'column': column,
            'dtype': str(df[column].dtype),
            'count': len(df[column]),
            'missing_count': df[column].isna().sum(),
            'missing_percent': float(df[column].isna().sum() / len(df[column]) if len(df[column]) > 0 else 0),
            'unique_count': df[column].nunique()
        }
    
    return profile
