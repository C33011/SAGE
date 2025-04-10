"""
Chart generation utilities for SAGE.

This module provides functions to generate different types of charts
for data quality reporting and visualization.
"""

import logging
import base64
import io
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np

# Set up logger
logger = logging.getLogger("sage.visualization.charts")

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    from matplotlib.colors import rgb2hex
    HAS_MATPLOTLIB = True
except ImportError:
    logger.warning("Matplotlib not available - static charts will be disabled")
    HAS_MATPLOTLIB = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import json
    HAS_PLOTLY = True
except ImportError:
    logger.warning("Plotly not available - interactive charts will be disabled")
    HAS_PLOTLY = False


def generate_completeness_chart(data: Dict[str, float], title: str = "Column Completeness") -> Optional[str]:
    """
    Generate a bar chart showing completeness scores by column.
    
    Args:
        data: Dictionary mapping column names to completeness scores
        title: Chart title
        
    Returns:
        Base64-encoded PNG image or None if visualization libraries aren't available
    """
    if not HAS_MATPLOTLIB:
        logger.warning("Matplotlib not available - cannot generate completeness chart")
        return None
    
    try:
        # Sort data by score for better visualization
        sorted_items = sorted(data.items(), key=lambda x: x[1])
        columns = [item[0] for item in sorted_items]
        scores = [item[1] for item in sorted_items]
        
        # Create color gradient based on scores
        colors = [_get_score_color(score) for score in scores]
        
        # Create the chart - increasing figure size slightly to avoid clipping text
        # FIXME: On some machines the text gets cut off. Might need a better solution.
        fig, ax = plt.subplots(figsize=(10, max(6, len(columns) * 0.4)))
        
        # TODO: Add option for vertical bars for presentations
        bars = ax.barh(columns, scores, color=colors)
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            label_x = width + 0.01
            ax.text(
                label_x,
                bar.get_y() + bar.get_height()/2,
                f'{width:.1%}',
                va='center'
            )
        
        # Set chart properties
        ax.set_xlim(0, 1.1)
        ax.set_xlabel('Completeness Score')
        ax.set_title(title)
        ax.grid(axis='x', alpha=0.3)
        
        # Add threshold lines if applicable
        ax.axvline(x=0.6, linestyle='--', color='#f44336', alpha=0.7, label='Failure Threshold')
        ax.axvline(x=0.8, linestyle='--', color='#ff9800', alpha=0.7, label='Warning Threshold')
        ax.legend()
        
        # Convert to base64 image
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error generating completeness chart: {str(e)}")
        return None

def _get_score_color(score: float) -> str:
    """
    Get color for a score based on thresholds.
    
    Args:
        score: The score value (0-1)
        
    Returns:
        Hex color code
    """
    if score >= 0.8:
        return '#4caf50'  # Green for good
    elif score >= 0.6:
        return '#ff9800'  # Orange for warning
    else:
        return '#f44336'  # Red for bad

def generate_accuracy_chart(data: Dict[str, Dict[str, int]], title: str = "Validation Results") -> Optional[str]:
    """
    Generate a stacked bar chart showing valid vs invalid counts by column.
    
    Args:
        data: Dictionary mapping column names to dicts with 'valid' and 'invalid' counts
        title: Chart title
        
    Returns:
        Base64-encoded PNG image or None if visualization libraries aren't available
    """
    if not HAS_MATPLOTLIB:
        logger.warning("Matplotlib not available - cannot generate accuracy chart")
        return None
    
    try:
        columns = list(data.keys())
        valid_counts = [data[col].get('valid', 0) for col in columns]
        invalid_counts = [data[col].get('invalid', 0) for col in columns]
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(10, max(6, len(columns) * 0.4)))
        
        # Create stacked bars
        ax.barh(columns, valid_counts, color='#4caf50', label='Valid')
        ax.barh(columns, invalid_counts, left=valid_counts, color='#f44336', label='Invalid')
        
        # Add data labels
        for i, column in enumerate(columns):
            total = valid_counts[i] + invalid_counts[i]
            if total > 0:
                # Add percentage label
                valid_pct = valid_counts[i] / total
                ax.text(
                    total + 0.5,
                    i,
                    f'{valid_pct:.1%} valid',
                    va='center'
                )
        
        # Set chart properties
        ax.set_xlabel('Count')
        ax.set_title(title)
        ax.grid(axis='x', alpha=0.3)
        ax.legend()
        
        # Convert to base64 image
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error generating accuracy chart: {str(e)}")
        return None


def generate_distribution_chart(data: pd.Series, title: str = None) -> Optional[str]:
    """
    Generate a histogram showing the distribution of values in a series.
    
    Args:
        data: Series of values to plot
        title: Chart title
        
    Returns:
        Base64 encoded PNG image, or None if Matplotlib is not available
    """
    if not HAS_MATPLOTLIB:
        return None
    
    try:
        # Create the figure
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Determine if data is numeric or categorical
        if pd.api.types.is_numeric_dtype(data):
            # For numeric data, create a histogram
            bins = min(30, len(data.dropna().unique()))
            ax.hist(data.dropna(), bins=bins, color='#4285f4', alpha=0.7)
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
        else:
            # For categorical data, create a bar chart of value counts
            value_counts = data.value_counts().head(15)  # Limit to top 15 values
            bars = ax.bar(value_counts.index.astype(str), value_counts.values, color='#4285f4')
            ax.set_ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            
            # Add data labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + 0.5,
                    str(int(height)),
                    ha='center',
                    va='bottom'
                )
        
        # Set title
        if title:
            ax.set_title(title)
        
        # Add grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Save to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error generating distribution chart: {e}")
        return None


def generate_interactive_distribution_chart(data: pd.Series, title: str = None) -> Optional[Dict[str, Any]]:
    """
    Generate an interactive Plotly chart showing distribution of values.
    
    Args:
        data: Series of values to plot
        title: Chart title
        
    Returns:
        Dictionary with Plotly figure data and layout
    """
    if not HAS_PLOTLY:
        return None
    
    try:
        # Determine if data is numeric or categorical
        if pd.api.types.is_numeric_dtype(data):
            # For numeric data, create a histogram
            fig = px.histogram(data.dropna(), nbins=30, title=title)
            fig.update_layout(
                xaxis_title="Value",
                yaxis_title="Frequency"
            )
        else:
            # For categorical data, create a bar chart of value counts
            value_counts = data.value_counts().head(15)  # Limit to top 15 values
            fig = px.bar(
                x=value_counts.index.astype(str),
                y=value_counts.values,
                title=title
            )
            fig.update_layout(
                xaxis_title=data.name,
                yaxis_title="Count"
            )
        
        # Common layout settings
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        # Convert to JSON
        return json.loads(fig.to_json())
    
    except Exception as e:
        logger.error(f"Error generating interactive distribution chart: {e}")
        return None


def generate_missing_values_heatmap(data: pd.DataFrame) -> Optional[str]:
    """
    Generate a heatmap showing missing values in the dataframe.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        Base64 encoded PNG image, or None if Matplotlib is not available
    """
    if not HAS_MATPLOTLIB:
        return None
    
    try:
        # Create a mask for missing values
        mask = data.isna()
        
        # Calculate % missing for each column
        missing_pct = mask.mean().sort_values(ascending=False)
        
        # Only show columns with missing values
        cols_with_missing = missing_pct[missing_pct > 0].index.tolist()
        
        if not cols_with_missing:
            return None
        
        # Subsample rows if there are too many
        max_rows = 100
        if len(data) > max_rows:
            # Sample rows, but ensure we include rows with missing values
            rows_with_missing = mask[cols_with_missing].any(axis=1)
            missing_idx = data[rows_with_missing].index
            
            # Calculate how many rows with missing values to include
            n_missing = min(int(max_rows * 0.7), len(missing_idx))
            
            # Calculate how many random rows to include
            n_random = max_rows - n_missing
            
            if n_random > 0:
                random_idx = data[~rows_with_missing].sample(n_random).index
                sampled_idx = missing_idx[:n_missing].union(random_idx)
            else:
                sampled_idx = missing_idx[:max_rows]
                
            sampled_data = data.loc[sampled_idx, cols_with_missing]
        else:
            sampled_data = data[cols_with_missing]
        
        # Create the figure
        fig_height = max(6, len(sampled_data) * 0.2)
        fig_width = max(8, len(cols_with_missing) * 0.5)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Plot the heatmap
        im = ax.imshow(sampled_data.isna(), aspect='auto', cmap='hot_r')
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Missing Value')
        
        # Customize axes
        ax.set_yticks(np.arange(len(sampled_data)))
        ax.set_xticks(np.arange(len(cols_with_missing)))
        ax.set_yticklabels([])  # Hide row labels
        ax.set_xticklabels(cols_with_missing, rotation=45, ha='right')
        
        # Add title and labels
        ax.set_title('Missing Values Heatmap')
        
        # Add missing percentage annotations
        for i, col in enumerate(cols_with_missing):
            pct = missing_pct[col] * 100
            ax.text(i, -0.5, f"{pct:.1f}%", ha='center', va='center', 
                   bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.3))
        
        # Add annotation about sampled data if applicable
        if len(data) > max_rows:
            fig.text(0.5, 0.01, f"Note: Showing a sample of {max_rows} out of {len(data)} rows", 
                     ha='center', fontsize=8, style='italic')
        
        # Save to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error generating missing values heatmap: {e}")
        return None


def generate_correlation_matrix(data: pd.DataFrame) -> Optional[str]:
    """
    Generate a correlation matrix heatmap for numeric columns.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        Base64 encoded PNG image, or None if Matplotlib is not available
    """
    if not HAS_MATPLOTLIB:
        return None
    
    try:
        # Extract numeric columns
        numeric_data = data.select_dtypes(include=['number'])
        
        if len(numeric_data.columns) < 2:
            return None
        
        # Calculate correlation matrix
        corr_matrix = numeric_data.corr()
        
        # Create the figure
        fig_size = max(6, len(corr_matrix) * 0.5)
        fig, ax = plt.subplots(figsize=(fig_size, fig_size))
        
        # Create heatmap
        im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Correlation')
        
        # Customize axes
        ax.set_xticks(np.arange(len(corr_matrix.columns)))
        ax.set_yticks(np.arange(len(corr_matrix.columns)))
        ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
        ax.set_yticklabels(corr_matrix.columns)
        
        # Add correlation values in cells
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                text_color = 'white' if abs(corr_value) > 0.5 else 'black'
                ax.text(j, i, f"{corr_value:.2f}", ha='center', va='center', color=text_color)
        
        # Add title
        ax.set_title('Correlation Matrix')
        
        # Save to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error generating correlation matrix: {e}")
        return None


def generate_summary_statistics_table(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics for a dataframe.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        Dictionary with summary statistics
    """
    try:
        stats = {
            'row_count': len(data),
            'column_count': len(data.columns),
            'missing_cells': int(data.isna().sum().sum()),
            'missing_percent': float(data.isna().sum().sum() / (len(data) * len(data.columns))),
            'duplicate_rows': int(data.duplicated().sum()),
            'duplicate_percent': float(data.duplicated().sum() / len(data) if len(data) > 0 else 0),
            'memory_usage_bytes': int(data.memory_usage(deep=True).sum()),
            'memory_usage_mb': float(data.memory_usage(deep=True).sum() / (1024 * 1024)),
            'column_types': {str(dtype): len(cols) for dtype, cols in data.dtypes.value_counts().items()}
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Error generating summary statistics: {e}")
        return {}
