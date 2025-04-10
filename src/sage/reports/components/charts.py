"""
Chart components for SAGE HTML reports.

This module provides functions to create and embed charts and visualizations
in HTML reports, using the visualization package functionality.
"""

import logging
from typing import Dict, List, Any, Optional, Union
import html
import uuid
import io
import base64

# Set up logger
logger = logging.getLogger("sage.reports.components.charts")

# Import visualization functions, with fallbacks for ImportErrors
try:
    from sage.visualization.chart_generators import (
        generate_bar_chart,
        generate_pie_chart,
        generate_line_chart,
        generate_quality_score_gauge,
        generate_column_quality_heatmap,
        generate_chart_html
    )
    
    from sage.visualization.data_formatters import (
        format_data_for_charts,
        prepare_categorical_data,
        prepare_timeseries_data
    )
    
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Visualization package not fully available: {str(e)}")
    VISUALIZATION_AVAILABLE = False

# Try to import matplotlib
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    logger.warning("Matplotlib not available - visualization will be disabled")
    HAS_MATPLOTLIB = False


def create_score_chart(scores: Dict[str, float],
                      title: Optional[str] = "Quality Scores",
                      id: Optional[str] = None,
                      class_name: str = "sage-chart",
                      chart_type: str = "bar",
                      width: int = 8,
                      height: int = 5) -> str:
    """
    Create a chart visualizing quality scores.
    
    Args:
        scores: Dictionary mapping metrics or columns to scores
        title: Chart title
        id: Optional HTML ID
        class_name: CSS class
        chart_type: Chart type ('bar', 'pie', 'gauge')
        width: Chart width in inches
        height: Chart height in inches
        
    Returns:
        HTML with embedded chart
    """
    if not VISUALIZATION_AVAILABLE:
        logger.warning("Visualization package not available, returning fallback HTML")
        return _create_fallback_chart_html(
            title=title,
            id=id,
            class_name=class_name,
            message="Visualization package not available"
        )
    
    try:
        # Generate unique ID if not provided
        chart_id = id or f"score-chart-{uuid.uuid4().hex[:8]}"
        
        # Create chart based on type
        if (chart_type == "pie"):
            chart_data = prepare_categorical_data(scores)
            img_data = generate_pie_chart(
                chart_data,
                title=title,
                width=width,
                height=height
            )
        elif chart_type == "gauge" and len(scores) == 1:
            # Gauge charts only work with a single score
            score_value = next(iter(scores.values()))
            img_data = generate_quality_score_gauge(
                score_value,
                title=title,
                width=width,
                height=height
            )
        else:
            # Default to bar chart
            chart_data = prepare_categorical_data(scores, sort_by="value")
            img_data = generate_bar_chart(
                chart_data,
                title=title,
                x_label="Category",
                y_label="Score",
                width=width,
                height=height
            )
            
        # Create the HTML
        return f"""
        <figure id="{chart_id}" class="{class_name}">
            <img src="{img_data}" alt="{html.escape(title)}" class="sage-chart-img">
            <figcaption>{html.escape(title)}</figcaption>
        </figure>
        """
    except Exception as e:
        logger.error(f"Error creating score chart: {str(e)}")
        return _create_fallback_chart_html(
            title=title,
            id=id,
            class_name=class_name,
            message=f"Error creating chart: {str(e)}"
        )


def create_completeness_chart(completeness_data: Dict[str, Union[float, Dict]],
                             title: Optional[str] = "Data Completeness",
                             id: Optional[str] = None,
                             class_name: str = "sage-chart",
                             width: int = 10,
                             height: int = 6) -> str:
    """
    Create a chart visualizing data completeness.
    
    Args:
        completeness_data: Completeness metric results
        title: Chart title
        id: Optional HTML ID
        class_name: CSS class
        width: Chart width in inches
        height: Chart height in inches
        
    Returns:
        HTML with embedded chart
    """
    if not VISUALIZATION_AVAILABLE:
        logger.warning("Visualization package not available, returning fallback HTML")
        return _create_fallback_chart_html(
            title=title,
            id=id,
            class_name=class_name,
            message="Visualization package not available"
        )
    
    try:
        # Generate unique ID if not provided
        chart_id = id or f"completeness-chart-{uuid.uuid4().hex[:8]}"
        
        # Extract column completeness scores
        column_scores = {}
        
        # Handle different completeness_data formats
        if "columns" in completeness_data and isinstance(completeness_data["columns"], dict):
            # Extract from standard completeness metric format
            for col, details in completeness_data["columns"].items():
                if isinstance(details, dict) and "completeness" in details:
                    column_scores[col] = details["completeness"]
        else:
            # Try to extract directly (simpler format)
            for key, value in completeness_data.items():
                if isinstance(value, dict) and "completeness" in value:
                    column_scores[key] = value["completeness"]
                elif isinstance(value, (int, float)) and 0 <= value <= 1:
                    column_scores[key] = value
        
        # If we couldn't extract column scores, use the top-level data
        if not column_scores and isinstance(completeness_data, dict):
            for key, value in completeness_data.items():
                if isinstance(value, (int, float)) and 0 <= value <= 1:
                    column_scores[key] = value
        
        # Sort by completeness score
        column_scores = dict(sorted(column_scores.items(), key=lambda x: x[1]))
        
        # Create horizontal bar chart for better readability with many columns
        img_data = generate_bar_chart(
            column_scores,
            title=title,
            x_label="Completeness",
            y_label="Column",
            horizontal=True,
            color="#228833",  # Green for completeness
            width=width,
            height=height
        )
            
        # Create the HTML
        return f"""
        <figure id="{chart_id}" class="{class_name}">
            <img src="{img_data}" alt="{html.escape(title)}" class="sage-chart-img">
            <figcaption>{html.escape(title)}</figcaption>
        </figure>
        """
    except Exception as e:
        logger.error(f"Error creating completeness chart: {str(e)}")
        return _create_fallback_chart_html(
            title=title,
            id=id,
            class_name=class_name,
            message=f"Error creating chart: {str(e)}"
        )


def create_distribution_chart(data: Dict[str, Any],
                             column: Optional[str] = None,
                             title: Optional[str] = None,
                             id: Optional[str] = None,
                             class_name: str = "sage-chart",
                             chart_type: str = "bar",
                             width: int = 8,
                             height: int = 5) -> str:
    """
    Create a chart visualizing the distribution of values.
    
    Args:
        data: Data with distribution information
        column: Optional column name (if data contains multiple columns)
        title: Chart title
        id: Optional HTML ID
        class_name: CSS class
        chart_type: Chart type ('bar', 'pie')
        width: Chart width in inches
        height: Chart height in inches
        
    Returns:
        HTML with embedded chart
    """
    if not VISUALIZATION_AVAILABLE:
        logger.warning("Visualization package not available, returning fallback HTML")
        return _create_fallback_chart_html(
            title=title or "Value Distribution",
            id=id,
            class_name=class_name,
            message="Visualization package not available"
        )
    
    try:
        # Generate unique ID if not provided
        chart_id = id or f"distribution-chart-{uuid.uuid4().hex[:8]}"
        
        # Extract the distribution data based on input format
        distribution = None
        
        if column and isinstance(data, dict) and column in data:
            # Data contains column-specific information
            col_data = data[column]
            
            if isinstance(col_data, dict):
                if "top_values" in col_data:
                    # Use top values for categorical data
                    distribution = col_data["top_values"]
                elif "histogram" in col_data and isinstance(col_data["histogram"], dict):
                    # Use histogram for numeric data
                    hist = col_data["histogram"]
                    if "counts" in hist and "bins" in hist:
                        # Create bin labels from bin edges
                        bins = hist["bins"]
                        counts = hist["counts"]
                        distribution = {}
                        for i, count in enumerate(counts):
                            if i < len(bins) - 1:
                                bin_label = f"{bins[i]:.1f}-{bins[i+1]:.1f}"
                                distribution[bin_label] = count
        elif isinstance(data, dict):
            # Try to use data directly as distribution
            if all(isinstance(v, (int, float)) for v in data.values()):
                distribution = data
        
        # If we couldn't extract distribution, return fallback
        if not distribution:
            return _create_fallback_chart_html(
                title=title or "Value Distribution",
                id=chart_id,
                class_name=class_name,
                message="Could not extract distribution data"
            )
        
        # Create chart based on type
        chart_title = title or (f"{column} Distribution" if column else "Value Distribution")
        
        if chart_type == "pie":
            img_data = generate_pie_chart(
                distribution,
                title=chart_title,
                width=width,
                height=height
            )
        else:
            # Default to bar chart
            img_data = generate_bar_chart(
                distribution,
                title=chart_title,
                x_label="Value",
                y_label="Count",
                width=width,
                height=height
            )
            
        # Create the HTML
        return f"""
        <figure id="{chart_id}" class="{class_name}">
            <img src="{img_data}" alt="{html.escape(chart_title)}" class="sage-chart-img">
            <figcaption>{html.escape(chart_title)}</figcaption>
        </figure>
        """
    except Exception as e:
        logger.error(f"Error creating distribution chart: {str(e)}")
        return _create_fallback_chart_html(
            title=title or "Value Distribution",
            id=id,
            class_name=class_name,
            message=f"Error creating chart: {str(e)}"
        )


def create_timeline_chart(time_data: Dict[str, List],
                         title: Optional[str] = "Timeline",
                         id: Optional[str] = None,
                         class_name: str = "sage-chart",
                         width: int = 10,
                         height: int = 6) -> str:
    """
    Create a timeline chart for time series data.
    
    Args:
        time_data: Time series data
        title: Chart title
        id: Optional HTML ID
        class_name: CSS class
        width: Chart width in inches
        height: Chart height in inches
        
    Returns:
        HTML with embedded chart
    """
    if not VISUALIZATION_AVAILABLE:
        logger.warning("Visualization package not available, returning fallback HTML")
        return _create_fallback_chart_html(
            title=title,
            id=id,
            class_name=class_name,
            message="Visualization package not available"
        )
    
    try:
        # Generate unique ID if not provided
        chart_id = id or f"timeline-chart-{uuid.uuid4().hex[:8]}"
        
        # Process the time data
        processed_data = prepare_timeseries_data(time_data)
        
        # Create the chart
        img_data = generate_line_chart(
            processed_data,
            title=title,
            x_label="Time",
            y_label="Value",
            width=width,
            height=height
        )
            
        # Create the HTML
        return f"""
        <figure id="{chart_id}" class="{class_name}">
            <img src="{img_data}" alt="{html.escape(title)}" class="sage-chart-img">
            <figcaption>{html.escape(title)}</figcaption>
        </figure>
        """
    except Exception as e:
        logger.error(f"Error creating timeline chart: {str(e)}")
        return _create_fallback_chart_html(
            title=title,
            id=id,
            class_name=class_name,
            message=f"Error creating chart: {str(e)}"
        )


def embed_chart(chart_html: str,
               title: Optional[str] = None,
               id: Optional[str] = None,
               class_name: str = "sage-chart-container") -> str:
    """
    Embed a chart in a standardized container.
    
    Args:
        chart_html: HTML chart content
        title: Optional title to display
        id: Optional HTML ID
        class_name: CSS class
        
    Returns:
        HTML with embedded chart
    """
    # Generate unique ID if not provided
    container_id = id or f"chart-container-{uuid.uuid4().hex[:8]}"
    
    # Create a standardized container
    html_parts = [f'<div id="{container_id}" class="{class_name}">']
    
    # Add title if provided
    if title:
        html_parts.append(f'<h3 class="chart-title">{html.escape(title)}</h3>')
    
    # Add the chart content
    html_parts.append(chart_html)
    
    # Close the container
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)


def _create_fallback_chart_html(title: str,
                              id: Optional[str] = None,
                              class_name: str = "sage-chart",
                              message: str = "Chart not available") -> str:
    """
    Create a fallback placeholder when charts cannot be generated.
    
    Args:
        title: Chart title
        id: Optional HTML ID
        class_name: CSS class
        message: Message to display
        
    Returns:
        Fallback HTML
    """
    chart_id = id or f"fallback-chart-{uuid.uuid4().hex[:8]}"
    
    return f"""
    <div id="{chart_id}" class="{class_name} chart-fallback">
        <div class="chart-fallback-content">
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(message)}</p>
        </div>
    </div>
    """


def generate_metric_summary_chart(metrics: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """
    Generate a summary chart of all metrics.
    
    Args:
        metrics: Dictionary mapping metric names to results
        
    Returns:
        Base64-encoded PNG image or None if visualization libraries aren't available
    """
    if not HAS_MATPLOTLIB:
        logger.warning("Matplotlib not available - cannot generate metric summary chart")
        return None
    
    try:
        # Extract metric names and scores
        metric_names = list(metrics.keys())
        scores = [m.get('score', 0) for m in metrics.values()]
        statuses = [m.get('status', 'failed') for m in metrics.values()]
        
        # Map statuses to colors
        colors = []
        for status in statuses:
            if status == 'passed':
                colors.append('#4caf50')  # Green
            elif status == 'warning':
                colors.append('#ff9800')  # Orange
            else:
                colors.append('#f44336')  # Red
        
        # Create the chart
        fig, ax = plt.subplots(figsize=(10, max(5, len(metric_names) * 0.5)))
        bars = ax.barh(metric_names, scores, color=colors)
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 0.01,
                bar.get_y() + bar.get_height()/2,
                f'{width:.1%}',
                va='center'
            )
        
        # Set chart properties
        ax.set_xlim(0, 1.1)
        ax.set_xlabel('Score')
        ax.set_title('Metric Scores')
        ax.grid(axis='x', alpha=0.3)
        
        # Add threshold indicators
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
        logger.error(f"Error generating metric summary chart: {str(e)}")
        return None
