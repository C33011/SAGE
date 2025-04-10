"""
HTML report generation for SAGE.

This module handles the creation of HTML reports from data quality
assessment results, including formatting, styling, and integration
of interactive elements.
"""

import os
import datetime
import logging
import jinja2
from typing import Dict, Any, Optional, List, Union
import base64
import json
import pandas as pd  # Add missing pandas import

# Set up logger
logger = logging.getLogger("sage.reports.html")

# Try to import visualization components
try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    from matplotlib.colors import rgb2hex
    import io
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    logger.warning("Matplotlib not available - charts will be disabled")
    HAS_MATPLOTLIB = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    logger.warning("Plotly not available - interactive charts will be disabled")
    HAS_PLOTLY = False


def _get_default_template() -> str:
    """
    Get the default HTML template for reports.
    
    Returns:
        HTML template string
    """
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'default.html')
    
    # Check if the template exists
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # If template file doesn't exist, return the inline template
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title|default('Data Quality Report') }}</title>
    <style>
        :root {
            --primary: #4285f4;
            --primary-light: #80b1ff;
            --primary-dark: #0d5bdd;
            --secondary: #34a853;
            --accent: #ea4335;
            --warning: #fbbc05;
            --background: #f8f9fa;
            --text: #202124;
            --text-light: #5f6368;
            --surface: #ffffff;
            --surface-2: #f1f3f4;
            --divider: #dadce0;
            --error: #d93025;
            --success: #188038;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: var(--text);
            background-color: var(--background);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: var(--primary);
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            margin-bottom: 30px;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center.
        }
        
        .overview {
            flex: 2;
            padding-right: 20px;
        }
        
        .score-display {
            flex: 1;
            text-align: center;
        }
        
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
            font-size: 2em;
            font-weight: bold;
            color: white;
            position: relative;
        }
        
        .score-high {
            background-color: var(--success);
        }
        
        .score-medium {
            background-color: var(--warning);
        }
        
        .score-low {
            background-color: var(--error);
        }
        
        h1, h2, h3, h4 {
            margin-bottom: 1rem;
            color: var(--primary-dark);
        }
        
        .header h1 {
            color: white;
            margin-bottom: 5px;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .section {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            padding: 20px;
            overflow: hidden.
        }
        
        .section h2 {
            padding-bottom: 10px;
            border-bottom: 1px solid var(--divider);
            margin-bottom: 20px.
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            grid-gap: 20px.
        }
        
        .card {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 15px;
            display: flex;
            flex-direction: column.
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px.
        }
        
        .card-icon {
            margin-right: 10px;
            font-size: 1.2em.
        }
        
        .status-passed { color: var(--success); }
        .status-warning { color: var(--warning); }
        .status-failed { color: var(--error); }
        
        .card-title {
            font-size: 1.1em;
            font-weight: bold.
        }
        
        .card-score {
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            margin: 10px 0.
        }
        
        .score-passed { color: var(--success); }
        .score-warning { color: var(--warning); }
        .score-failed { color: var(--error); }
        
        .card-message {
            margin-top: auto;
            font-size: 0.9em;
            color: var(--text-light).
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px.
        }
        
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--divider).
        }
        
        th {
            background-color: var(--surface-2);
            font-weight: bold.
        }
        
        tr:hover {
            background-color: var(--surface-2).
        }
        
        .chart-container {
            width: 100%;
            margin: 20px 0;
            text-align: center.
        }
        
        .chart {
            max-width: 100%;
            height: auto.
        }
        
        .recommendations {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            padding: 20px.
        }
        
        .recommendation {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--divider).
        }
        
        .recommendation:last-child {
            border-bottom: none.
        }
        
        .recommendation h3 {
            margin-bottom: 10px;
            color: var(--text).
        }
        
        .priority-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 10px.
        }
        
        .priority-high {
            background-color: var(--error);
            color: white.
        }
        
        .priority-medium {
            background-color: var(--warning);
            color: white.
        }
        
        .priority-low {
            background-color: var(--success);
            color: white.
        }
        
        .recommendation-steps {
            margin-top: 10px;
            margin-left: 20px.
        }
        
        .recommendation-steps li {
            margin-bottom: 5px.
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: var(--text-light);
            font-size: 0.9em.
        }
        
        /* Data Profiling Styles */
        .profile-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px.
        }
        
        .profile-card {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 15px;
            flex: 1 1 300px.
        }
        
        .profile-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--divider);
            padding-bottom: 10px;
            margin-bottom: 15px.
        }
        
        .profile-title {
            font-weight: bold;
            font-size: 1.1em.
        }
        
        .profile-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px.
        }
        
        .stat-group {
            margin-bottom: 10px.
        }
        
        .stat-label {
            font-size: 0.85em;
            color: var(--text-light).
        }
        
        .stat-value {
            font-weight: bold.
        }
        
        .sample-values {
            margin-top: 15px;
            border-top: 1px solid var(--divider);
            padding-top: 10px.
        }
        
        .sample-values-title {
            font-size: 0.9em;
            margin-bottom: 5px.
        }
        
        .sample-list {
            font-size: 0.85em;
            display: flex;
            flex-wrap: wrap;
            gap: 8px.
        }
        
        .sample-item {
            background-color: var(--surface-2);
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block.
        }
        
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--divider);
            margin-bottom: 20px.
        }
        
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent.
        }
        
        .tab.active {
            border-bottom-color: var(--primary);
            font-weight: bold.
        }
        
        .tab-content {
            display: none.
        }
        
        .tab-content.active {
            display: block.
        }
        
        /* Interactive Chart Container */
        .interactive-chart {
            height: 400px;
            width: 100%;
            border: 1px solid var(--divider);
            border-radius: 8px;
            overflow: hidden.
        }
        
        /* Distribution chart styling */
        .distribution-chart {
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
            height: 200px.
        }
        
        /* Tooltip styling */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help.
        }
        
        .tooltip .tooltip-text {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s.
        }
        
        .tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1.
        }
        
        /* Fixes for mobile */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column.
            }
            
            .overview {
                padding-right: 0;
                margin-bottom: 20px.
            }
            
            .grid {
                grid-template-columns: 1fr.
            }
            
            .profile-container {
                flex-direction: column.
            }
        }
    </style>
    {% if has_plotly %}
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    {% endif %}
</head>
<body>
    <div class="container">
        <header>
            <div class="header-content">
                <div class="overview">
                    <h1>{{ title|default('Data Quality Report') }}</h1>
                    <p>{{ description|default('Assessment of data quality metrics') }}</p>
                    <p><small>Generated on {{ now|date("%Y-%m-%d %H:%M") }}</small></p>
                </div>
                <div class="score-display">
                    <div class="score-circle {% if overall_score > 0.9 %}score-high{% elif overall_score > 0.7 %}score-medium{% else %}score-low{% endif %}">
                        {{ overall_score|percent }}
                    </div>
                    <p>Overall Quality</p>
                </div>
            </div>
        </header>

        <!-- SUMMARY SECTION -->
        <section class="section">
            <h2>Quality Metrics Summary</h2>
            <div class="grid">
                {% for name, metric in metrics.items() %}
                <div class="card">
                    <div class="card-header">
                        <div class="card-icon status-{{ metric.status }}">
                            {% if metric.status == 'passed' %}✓
                            {% elif metric.status == 'warning' %}⚠
                            {% elif metric.status == 'failed' %}✗
                            {% else %}?{% endif %}
                        </div>
                        <div class="card-title">{{ name|title }}</div>
                    </div>
                    <div class="card-score score-{{ metric.status }}">{{ metric.score|percent }}</div>
                    <div class="card-message">{{ metric.message|default('') }}</div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- DATA PROFILING SECTION -->
        {% if profile_data and column_profiles %}
        <section class="section">
            <h2>Data Profiling</h2>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('overview-tab')">Overview</div>
                <div class="tab" onclick="showTab('column-profiles-tab')">Column Profiles</div>
            </div>
            
            <div id="overview-tab" class="tab-content active">
                <!-- Dataset overview -->
                <div class="profile-container">
                    <div class="profile-card">
                        <div class="profile-header">
                            <div class="profile-title">Dataset Summary</div>
                        </div>
                        <div class="profile-stats">
                            <div class="stat-group">
                                <div class="stat-label">Rows</div>
                                <div class="stat-value">{{ profile_data.row_count|default(0) }}</div>
                            </div>
                            <div class="stat-group">
                                <div class="stat-label">Columns</div>
                                <div class="stat-value">{{ profile_data.column_count|default(0) }}</div>
                            </div>
                            <div class="stat-group">
                                <div class="stat-label">Missing Cells</div>
                                <div class="stat-value">{{ profile_data.missing_cells|default(0) }} ({{ profile_data.missing_percent|default(0)|percent }})</div>
                            </div>
                            <div class="stat-group">
                                <div class="stat-label">Duplicate Rows</div>
                                <div class="stat-value">{{ profile_data.duplicate_rows|default(0) }} ({{ profile_data.duplicate_percent|default(0)|percent }})</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="profile-card">
                        <div class="profile-header">
                            <div class="profile-title">Column Types</div>
                        </div>
                        
                        <div class="chart-container">
                            {% if profile_data.type_chart %}
                            <img class="chart" src="data:image/png;base64,{{ profile_data.type_chart }}" alt="Column Types">
                            {% endif %}
                        </div>
                    </div>
                </div>
                
                <!-- Missing values overview -->
                <div class="profile-card">
                    <div class="profile-header">
                        <div class="profile-title">Missing Values</div>
                    </div>
                    
                    <div class="chart-container">
                        {% if profile_data.missing_chart %}
                        <img class="chart" src="data:image/png;base64,{{ profile_data.missing_chart }}" alt="Missing Values">
                        {% endif %}
                    </div>
                </div>
            </div>
            
            <div id="column-profiles-tab" class="tab-content">
                <!-- Individual column profiles -->
                <div class="profile-container">
                    {% for column, profile in column_profiles.items() %}
                    <div class="profile-card">
                        <div class="profile-header">
                            <div class="profile-title">{{ column }}</div>
                            <small>{{ profile.dtype }}</small>
                        </div>
                        <div class="profile-stats">
                            <div class="stat-group">
                                <div class="stat-label">Missing</div>
                                <div class="stat-value">{{ profile.missing_percent|percent }}</div>
                            </div>
                            <div class="stat-group">
                                <div class="stat-label">Unique</div>
                                <div class="stat-value">{{ profile.unique_values }}</div>
                            </div>
                            {% if profile.is_numeric %}
                            <div class="stat-group">
                                <div class="stat-label">Min</div>
                                <div class="stat-value">{{ profile.min }}</div>
                            </div>
                            <div class="stat-group">
                                <div class="stat-label">Max</div>
                                <div class="stat-value">{{ profile.max }}</div>
                            </div>
                            <div class="stat-group">
                                <div class="stat-label">Mean</div>
                                <div class="stat-value">{{ profile.mean }}</div>
                            </div>
                            <div class="stat-group">
                                <div class="stat-label">Median</div>
                                <div class="stat-value">{{ profile.median }}</div>
                            </div>
                            {% endif %}
                        </div>
                        
                        {% if profile.distribution_chart %}
                        <div class="chart-container">
                            <img class="chart" src="data:image/png;base64,{{ profile.distribution_chart }}" alt="Distribution of {{ column }}">
                        </div>
                        {% endif %}
                        
                        <div class="sample-values">
                            <div class="sample-values-title">Sample Values:</div>
                            <div class="sample-list">
                                {% for value in profile.sample_values %}
                                <span class="sample-item">{{ value }}</span>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </section>
        {% endif %}
        
        <!-- DETAILED RESULTS SECTION -->
        {% if details %}
        <section class="section">
            <h2>Detailed Results</h2>
            
            {% for metric_name, metric_details in metrics.items() %}
            {% if metric_details.columns %}
            <h3>{{ metric_name|title }} Details</h3>
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for col, col_data in metric_details.columns.items() %}
                    <tr>
                        <td>{{ col }}</td>
                        <td>{{ col_data.score|default(col_data.completeness)|percent }}</td>
                        <td class="status-{{ col_data.status }}">{{ col_data.status }}</td>
                        <td>{{ col_data.message|default('') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            
            {% if metric_details.details %}
            <h3>{{ metric_name|title }} Details</h3>
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Valid</th>
                        <th>Invalid</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for col, col_data in metric_details.details.items() %}
                    <tr>
                        <td>{{ col }}</td>
                        <td>{{ col_data.valid|default(0) }}</td>
                        <td>{{ col_data.invalid|default(0) }}</td>
                        <td>{{ col_data.message|default('') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            {% endfor %}
            
            {% for key, value in details.items() %}
            {% if key not in ['columns', 'tables'] %}
            <h3>{{ key|title }}</h3>
            {% if value is mapping %}
                <table>
                    <tbody>
                        {% for k, v in value.items() %}
                        <tr>
                            <td>{{ k|title }}</td>
                            <td>{{ v }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>{{ value }}</p>
            {% endif %}
            {% endif %}
            {% endfor %}
        </section>
        {% endif %}
        
        <!-- RECOMMENDATIONS SECTION -->
        {% if recommendations %}
        <section class="section">
            <h2>Recommendations</h2>
            
            {% for rec in recommendations %}
            <div class="recommendation">
                <h3>{{ rec.title }}</h3>
                <div class="priority-tag priority-{{ rec.priority }}">{{ rec.priority|title }} Priority</div>
                <p>{{ rec.description }}</p>
                {% if rec.steps %}
                <ul class="recommendation-steps">
                    {% for step in rec.steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </section>
        {% endif %}
        
        <footer>
            <p>Generated by SAGE - Spreadsheet Analysis Grading Engine</p>
            <p>{{ version|default('Version 0.1.0') }}</p>
        </footer>
    </div>
    
    <!-- Scripts -->
    <script>
        // Tab switching functionality
        function showTab(tabId) {
            // Hide all tab contents
            var tabContents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }
            
            // Deactivate all tabs
            var tabs = document.getElementsByClassName('tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            
            // Show the selected tab content
            document.getElementById(tabId).classList.add('active');
            
            // Activate the clicked tab
            event.target.classList.add('active');
        }
        
        {% if has_plotly and plotly_charts %}
        // Initialize Plotly charts
        document.addEventListener('DOMContentLoaded', function() {
            {% for div_id, chart_json in plotly_charts.items() %}
            Plotly.newPlot('{{ div_id }}', {{ chart_json|safe }}.data, {{ chart_json|safe }}.layout);
            {% endfor %}
        });
        {% endif %}
    </script>
</body>
</html>
"""


def generate_data_profile(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a profile of the dataframe with summary statistics.
    
    Args:
        data: DataFrame to profile
        
    Returns:
        Dictionary with profile information
    """
    if data is None or data.empty:
        return {}
    
    # Basic dataset statistics
    profile = {
        'row_count': len(data),
        'column_count': len(data.columns),
        'missing_cells': data.isna().sum().sum(),
        'missing_percent': data.isna().sum().sum() / (len(data) * len(data.columns)),
        'duplicate_rows': data.duplicated().sum(),
        'duplicate_percent': data.duplicated().sum() / len(data) if len(data) > 0 else 0
    }
    
    # Generate column type chart if matplotlib is available
    if HAS_MATPLOTLIB:
        type_counts = {
            'Numeric': len([col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]),
            'Text': len([col for col in data.columns if pd.api.types.is_string_dtype(data[col])]),
            'Boolean': len([col for col in data.columns if pd.api.types.is_bool_dtype(data[col])]),
            'Datetime': len([col for col in data.columns if pd.api.types.is_datetime64_dtype(data[col])]),
            'Categorical': len([col for col in data.columns if pd.api.types.is_categorical_dtype(data[col])]),
            'Other': len([col for col in data.columns if not (
                pd.api.types.is_numeric_dtype(data[col]) or
                pd.api.types.is_string_dtype(data[col]) or
                pd.api.types.is_bool_dtype(data[col]) or
                pd.api.types.is_datetime64_dtype(data[col]) or
                pd.api.types.is_categorical_dtype(data[col])
            )])
        }
        
        # Filter out zero values
        type_counts = {k: v for k, v in type_counts.items() if v > 0}
        
        plt.figure(figsize=(6, 4))
        plt.pie(
            list(type_counts.values()),
            labels=list(type_counts.keys()),
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.tab10.colors[:len(type_counts)]
        )
        plt.axis('equal')
        plt.title('Column Types')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        profile['type_chart'] = base64.b64encode(buf.read()).decode('utf-8')
        
        # Generate missing values chart
        missing_counts = data.isna().sum().sort_values(ascending=False)
        if missing_counts.sum() > 0:
            top_missing = missing_counts[missing_counts > 0]
            if len(top_missing) > 0:
                plt.figure(figsize=(10, 6))
                ax = top_missing.plot(kind='bar', color='#ff9999')
                plt.title('Missing Values by Column')
                plt.xlabel('Column')
                plt.ylabel('Missing Value Count')
                plt.xticks(rotation=45, ha='right')
                
                # Add data labels on top of bars
                for i, v in enumerate(top_missing):
                    ax.text(i, v + 0.5, str(v), ha='center')
                
                plt.tight_layout()
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()
                buf.seek(0)
                profile['missing_chart'] = base64.b64encode(buf.read()).decode('utf-8')
    
    return profile


def generate_column_profiles(data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Generate detailed profiles for each column with statistics and visualizations.
    
    Args:
        data: DataFrame to profile
        
    Returns:
        Dictionary with column profiles
    """
    if data is None or data.empty:
        return {}
    
    column_profiles = {}
    
    for column in data.columns:
        col_data = data[column]
        is_numeric = pd.api.types.is_numeric_dtype(col_data)
        
        # Basic statistics for all columns
        profile = {
            'dtype': str(col_data.dtype),
            'missing_count': col_data.isna().sum(),
            'missing_percent': col_data.isna().sum() / len(col_data) if len(col_data) > 0 else 0,
            'unique_values': col_data.nunique(),
            'is_numeric': is_numeric,
            'sample_values': col_data.dropna().sample(min(5, len(col_data.dropna()))).tolist() if not col_data.empty else []
        }
        
        # Additional statistics for numeric columns
        if is_numeric:
            profile.update({
                'min': col_data.min() if not col_data.empty else None,
                'max': col_data.max() if not col_data.empty else None,
                'mean': col_data.mean() if not col_data.empty else None,
                'median': col_data.median() if not col_data.empty else None,
                'std': col_data.std() if not col_data.empty else None
            })
            
            # Generate distribution chart for numeric columns
            if HAS_MATPLOTLIB and not col_data.dropna().empty:
                # Increase figure height to avoid tight layout warning
                plt.figure(figsize=(5, 4))  # Changed from (5, 3) to (5, 4)
                plt.hist(col_data.dropna(), bins=20, alpha=0.7, color='#4285f4')
                plt.title(f'Distribution of {column}')
                plt.xlabel(column)
                plt.ylabel('Frequency')
                # Add more bottom margin to accommodate x-labels
                plt.subplots_adjust(bottom=0.2)
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()
                buf.seek(0)
                profile['distribution_chart'] = base64.b64encode(buf.read()).decode('utf-8')
        
        # For categorical/text columns, show value counts
        elif col_data.dtype == 'object' or pd.api.types.is_categorical_dtype(col_data):
            value_counts = col_data.value_counts().head(10)
            if not value_counts.empty and HAS_MATPLOTLIB:
                # Increase figure height to avoid tight layout warning
                plt.figure(figsize=(5, 4))  # Changed from (5, 3) to (5, 4)
                ax = value_counts.plot(kind='bar', color='#4285f4')
                plt.title(f'Top values in {column}')
                plt.xlabel(column)
                plt.ylabel('Count')
                plt.xticks(rotation=45, ha='right')
                
                # Add more bottom margin to accommodate x-labels
                plt.subplots_adjust(bottom=0.3)
                
                # Add data labels on top of bars
                for i, v in enumerate(value_counts):
                    ax.text(i, v + 0.1, str(v), ha='center')
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                profile['distribution_chart'] = base64.b64encode(buf.read()).decode('utf-8')
            
            # Store top values
            profile['top_values'] = dict(value_counts)
        
        column_profiles[column] = profile
    
    return column_profiles


def generate_html_report(data: Dict[str, Any], output_path: str, template_path: Optional[str] = None) -> bool:
    """
    Generate an HTML report from data quality assessment results.
    
    Args:
        data: Assessment results and metadata
        output_path: Path to write the output HTML file
        template_path: Path to a custom HTML template (uses default if None)
        
    Returns:
        True if the report was generated successfully
    """
    try:
        logger.info(f"Generating HTML report at: {output_path}")
        
        # Get template content
        if template_path and os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_str = f.read()
                logger.debug(f"Using custom template: {template_path}")
        else:
            # Fall back to default template if custom one isn't provided
            # This template is embedded in the code to make deployment easier
            template_str = _get_default_template()
            logger.debug("Using default template")
        
        # Set up Jinja environment for templating
        env = jinja2.Environment()
        
        # Add custom filters for data formatting
        env.filters['date'] = lambda d, format='%Y-%m-%d': d.strftime(format) if isinstance(d, (datetime.date, datetime.datetime)) else d
        env.filters['percent'] = lambda f: f'{f:.1%}' if isinstance(f, (int, float)) else f
        
        # The filter approach is cleaner than doing this formatting in Python code
        # before passing to the template
        
        # Create template
        template = env.from_string(template_str)
        
        # Determine overall score if not provided
        if 'overall_score' not in data and 'metrics' in data:
            metrics = data.get('metrics', {})
            scores = []
            
            for metric_name, metric_data in metrics.items():
                if 'score' in metric_data:
                    scores.append(metric_data['score'])
            
            if scores:
                data['overall_score'] = sum(scores) / len(scores)
                
                # Determine overall status
                if data['overall_score'] >= 0.9:
                    data['overall_status'] = 'passed'
                elif data['overall_score'] >= 0.7:
                    data['overall_status'] = 'warning'
                else:
                    data['overall_status'] = 'failed'
            else:
                data['overall_score'] = 0
                data['overall_status'] = 'unknown'
        
        # Generate data profile if data sources are available
        profile_data = {}
        column_profiles = {}
        
        # Check if a DataFrame is available to profile
        df = None
        
        # Check for DataFrame from excel_grader or database_grader
        if 'metadata' in data:
            if 'grader' in data['metadata'] and hasattr(data['metadata']['grader'], 'get_active_data'):
                df = data['metadata']['grader'].get_active_data()
            elif 'excel' in data['metadata'] and 'file_path' in data['metadata']['excel']:
                try:
                    excel_path = data['metadata']['excel']['file_path']
                    sheet_name = data['metadata']['excel']['active_sheet']
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                except Exception as e:
                    logger.warning(f"Could not load Excel data for profiling: {e}")
            elif 'database' in data['metadata'] and 'table' in data['metadata']['database']:
                # Database data would require more complex handling - skipping for now
                pass
        
        if df is not None:
            try:
                # Generate profiles
                profile_data = generate_data_profile(df)
                column_profiles = generate_column_profiles(df)
            except Exception as e:
                logger.warning(f"Error generating data profiles: {e}")
                # Don't let profiling errors prevent report generation
                profile_data = {}
                column_profiles = {}
        
        # Add profile data to template variables
        template_vars = {
            'now': datetime.datetime.now(),
            'version': '0.1.0',  # Should be pulled from package version
            'has_matplotlib': HAS_MATPLOTLIB,
            'has_plotly': HAS_PLOTLY,
            'profile_data': profile_data,
            'column_profiles': column_profiles,
            **data
        }
        
        # Render template
        html_output = template.render(**template_vars)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
            
        logger.info(f"HTML report generated successfully at: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        logger.exception(e)
        return False
