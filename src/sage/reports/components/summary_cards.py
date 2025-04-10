"""
Summary card generators for SAGE reports.

This module provides functions to generate HTML summary cards
for data quality reports.
"""

import logging
from typing import Dict, Any, List, Optional
import json

# Set up logger
logger = logging.getLogger("sage.reports.components.cards")


def generate_metric_card(name: str, metric_data: Dict[str, Any]) -> str:
    """
    Generate HTML for a metric summary card.
    
    Args:
        name: Metric name
        metric_data: Metric data dictionary
        
    Returns:
        HTML string for the card
    """
    score = metric_data.get('score', 0)
    status = metric_data.get('status', 'unknown')
    message = metric_data.get('message', '')
    
    # Determine status icon
    if status == 'passed':
        icon = '✓'
    elif status == 'warning':
        icon = '⚠'
    elif status == 'failed':
        icon = '✗'
    else:
        icon = '?'
    
    # Format score as percentage
    score_str = f"{score:.1%}" if isinstance(score, (int, float)) else str(score)
    
    html = f"""
    <div class="card">
        <div class="card-header">
            <div class="card-icon status-{status}">{icon}</div>
            <div class="card-title">{name.title()}</div>
        </div>
        <div class="card-score score-{status}">{score_str}</div>
        <div class="card-message">{message}</div>
    </div>
    """
    
    return html


def generate_profile_card(column: str, profile_data: Dict[str, Any]) -> str:
    """
    Generate HTML for a column profile card.
    
    Args:
        column: Column name
        profile_data: Column profile data
        
    Returns:
        HTML string for the card
    """
    dtype = profile_data.get('dtype', '')
    missing_percent = profile_data.get('missing_percent', 0)
    unique_values = profile_data.get('unique_values', 0)
    is_numeric = profile_data.get('is_numeric', False)
    sample_values = profile_data.get('sample_values', [])
    
    # Format missing percentage
    missing_str = f"{missing_percent:.1%}" if isinstance(missing_percent, (int, float)) else str(missing_percent)
    
    # Start building HTML
    html = f"""
    <div class="profile-card">
        <div class="profile-header">
            <div class="profile-title">{column}</div>
            <small>{dtype}</small>
        </div>
        <div class="profile-stats">
            <div class="stat-group">
                <div class="stat-label">Missing</div>
                <div class="stat-value">{missing_str}</div>
            </div>
            <div class="stat-group">
                <div class="stat-label">Unique</div>
                <div class="stat-value">{unique_values}</div>
            </div>
    """
    
    # Add numeric statistics if available
    if is_numeric:
        min_val = profile_data.get('min', '')
        max_val = profile_data.get('max', '')
        mean_val = profile_data.get('mean', '')
        median_val = profile_data.get('median', '')
        
        html += f"""
            <div class="stat-group">
                <div class="stat-label">Min</div>
                <div class="stat-value">{min_val}</div>
            </div>
            <div class="stat-group">
                <div class="stat-label">Max</div>
                <div class="stat-value">{max_val}</div>
            </div>
            <div class="stat-group">
                <div class="stat-label">Mean</div>
                <div class="stat-value">{mean_val}</div>
            </div>
            <div class="stat-group">
                <div class="stat-label">Median</div>
                <div class="stat-value">{median_val}</div>
            </div>
        """
    
    # Close stats div
    html += "</div>"
    
    # Add distribution chart if available
    if 'distribution_chart' in profile_data:
        html += f"""
        <div class="chart-container">
            <img class="chart" src="data:image/png;base64,{profile_data['distribution_chart']}" alt="Distribution of {column}">
        </div>
        """
    
    # Add sample values
    html += """
        <div class="sample-values">
            <div class="sample-values-title">Sample Values:</div>
            <div class="sample-list">
    """
    
    # Add each sample value
    for value in sample_values:
        html += f'<span class="sample-item">{value}</span>'
    
    # Close remaining divs
    html += """
            </div>
        </div>
    </div>
    """
    
    return html


def generate_recommendation_card(recommendation: Dict[str, Any]) -> str:
    """
    Generate HTML for a recommendation card.
    
    Args:
        recommendation: Recommendation data
        
    Returns:
        HTML string for the card
    """
    title = recommendation.get('title', '')
    priority = recommendation.get('priority', 'medium')
    description = recommendation.get('description', '')
    steps = recommendation.get('steps', [])
    
    html = f"""
    <div class="recommendation">
        <h3>{title}</h3>
        <div class="priority-tag priority-{priority}">{priority.title()} Priority</div>
        <p>{description}</p>
    """
    
    # Add steps if available
    if steps:
        html += '<ul class="recommendation-steps">'
        for step in steps:
            html += f'<li>{step}</li>'
        html += '</ul>'
    
    html += "</div>"
    
    return html
