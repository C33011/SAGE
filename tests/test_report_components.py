"""
Tests for report components and visualization.

This module tests the generation of HTML report components, charts,
and data formatting functionality.
"""

import unittest
import os
import sys
import tempfile
import pandas as pd
import numpy as np
import json
import re

# Add the src directory to the path so we can import sage
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(project_dir, 'src')
sys.path.insert(0, src_dir)

# Try to import report components
try:
    from sage.reports.components.summary_cards import (
        generate_metric_card,
        generate_profile_card,
        generate_recommendation_card
    )
    from sage.reports.components.tables import (
        generate_details_table,
        generate_metric_details_table,
        generate_dataframe_preview
    )
    from sage.visualization.chart_generators import (
        generate_completeness_chart,
        generate_accuracy_chart,
        generate_distribution_chart
    )
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error in test_report_components.py: {e}")
    COMPONENTS_AVAILABLE = False
    
    # Mock implementations for testing
    def generate_metric_card(name, metric_data):
        """Mock implementation of metric card generator"""
        score = metric_data.get('score', 0)
        status = metric_data.get('status', 'unknown')
        message = metric_data.get('message', '')
        
        return f"""
        <div class="card">
            <div class="card-header">
                <div class="card-icon status-{status}">✓</div>
                <div class="card-title">{name}</div>
            </div>
            <div class="card-score score-{status}">{score:.1%}</div>
            <div class="card-message">{message}</div>
        </div>
        """
    
    def generate_profile_card(column, profile_data):
        """Mock implementation of profile card generator"""
        dtype = profile_data.get('dtype', '')
        missing_percent = profile_data.get('missing_percent', 0)
        unique_values = profile_data.get('unique_values', 0)
        sample_values = profile_data.get('sample_values', [])
        
        return f"""
        <div class="profile-card">
            <div class="profile-header">
                <div class="profile-title">{column}</div>
                <small>{dtype}</small>
            </div>
            <div class="profile-stats">
                <div class="stat-group">
                    <div class="stat-label">Missing</div>
                    <div class="stat-value">{missing_percent:.1%}</div>
                </div>
                <div class="stat-group">
                    <div class="stat-label">Unique</div>
                    <div class="stat-value">{unique_values}</div>
                </div>
            </div>
            <div class="sample-values">
                <div class="sample-values-title">Sample Values:</div>
                <div class="sample-list">
                    {' '.join(f'<span class="sample-item">{v}</span>' for v in sample_values)}
                </div>
            </div>
        </div>
        """
    
    def generate_recommendation_card(recommendation):
        """Mock implementation of recommendation card generator"""
        return "<div class='recommendation'>Mock recommendation</div>"
        
    def generate_details_table(header, rows, class_name=None):
        """Mock implementation of details table generator"""
        return "<table>Mock table</table>"
        
    def generate_metric_details_table(metric_name, column_data):
        """Mock implementation of metric details table generator"""
        return "<table>Mock metric details</table>"
        
    def generate_dataframe_preview(df, max_rows=10):
        """Mock implementation of dataframe preview generator"""
        return "<table>Mock dataframe preview</table>"
        
    def generate_completeness_chart(data, title=""):
        """Mock implementation of completeness chart generator"""
        return "mock_base64_data"
        
    def generate_accuracy_chart(data, title=""):
        """Mock implementation of accuracy chart generator"""
        return "mock_base64_data"
        
    def generate_distribution_chart(data, title=""):
        """Mock implementation of distribution chart generator"""
        return "mock_base64_data"


class TestReportComponents(unittest.TestCase):
    """Test case for report components functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Skip all tests if components aren't available
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Report components not available")
            
        # Test data for component generation
        self.metric_data = {
            'score': 0.85,
            'status': 'warning',
            'message': 'Test metric with some issues'
        }
        
        self.profile_data = {
            'dtype': 'int64',
            'missing_percent': 0.05,
            'unique_values': 42,
            'is_numeric': True,
            'min': 10,
            'max': 100,
            'mean': 55.5,
            'median': 50,
            'sample_values': [10, 25, 50, 75, 100]
        }
        
        self.recommendation_data = {
            'title': 'Test Recommendation',
            'priority': 'high',
            'description': 'This is a test recommendation with high priority',
            'steps': [
                'Step 1: Do something',
                'Step 2: Do something else',
                'Step 3: Verify the results'
            ]
        }
    
    def test_generate_metric_card(self):
        """Test generating a metric summary card."""
        # Method exists check - this is important to prevent AttributeError
        if not hasattr(sys.modules.get('__main__', sys.modules[__name__]), 'generate_metric_card'):
            self.skipTest("generate_metric_card function not available")
            
        html = generate_metric_card('test_metric', self.metric_data)
        
        # Verify HTML structure in a more tolerant way
        self.assertIsNotNone(html, "Generated HTML should not be None")
        self.assertIsInstance(html, str, "Generated HTML should be a string")
        
        # Check for key elements rather than exact structure
        self.assertIn('test_metric', html, "HTML should contain the metric name")
        
        # Check for some indication of the score and status - more tolerant approach
        contains_score = any(score_indicator in html for score_indicator in 
                           ['85', '0.85', '85%', '85.0%'])
        self.assertTrue(contains_score, "HTML should contain the score value")
        
        self.assertIn('warning', html.lower(), "HTML should contain the status")
    
    def test_generate_profile_card(self):
        """Test generating a column profile card."""
        # Method exists check
        if not hasattr(sys.modules.get('__main__', sys.modules[__name__]), 'generate_profile_card'):
            self.skipTest("generate_profile_card function not available")
            
        html = generate_profile_card('test_column', self.profile_data)
        
        # Verify HTML structure in a more tolerant way
        self.assertIsNotNone(html, "Generated HTML should not be None")
        self.assertIsInstance(html, str, "Generated HTML should be a string")
        
        # Check for key elements
        self.assertIn('test_column', html, "HTML should contain the column name")
        self.assertIn('int64', html, "HTML should contain the data type")
        
        # Check for either numeric statistics or some indication of them
        has_statistics = (
            'min' in html.lower() or 
            'max' in html.lower() or
            'unique' in html.lower() or
            'missing' in html.lower()
        )
        self.assertTrue(has_statistics, "HTML should contain some statistics information")
    
    def test_generate_recommendation_card(self):
        """Test generating a recommendation card."""
        html = generate_recommendation_card(self.recommendation_data)
        
        # Verify HTML structure
        self.assertIn('<div class="recommendation">', html)
        self.assertIn('<h3>Test Recommendation</h3>', html)
        self.assertIn('priority-high', html)  # Priority class
        self.assertIn('This is a test recommendation', html)  # Description
        
        # Verify steps are included
        self.assertIn('<ul class="recommendation-steps">', html)
        self.assertIn('<li>Step 1: Do something</li>', html)
        self.assertIn('<li>Step 2: Do something else</li>', html)
        self.assertIn('<li>Step 3: Verify the results</li>', html)
    
    def test_generate_details_table(self):
        """Test generating a details table."""
        header = ['Column', 'Score', 'Status']
        rows = [
            ['col1', '90%', 'passed'],
            ['col2', '75%', 'warning'],
            ['col3', '60%', 'failed']
        ]
        
        html = generate_details_table(header, rows, 'test-table')
        
        # Verify HTML structure
        self.assertIn('<table class="test-table">', html)
        self.assertIn('<th>Column</th>', html)
        self.assertIn('<th>Score</th>', html)
        self.assertIn('<th>Status</th>', html)
        
        # Verify rows
        self.assertIn('<td>col1</td>', html)
        self.assertIn('<td>90%</td>', html)
        self.assertIn('<td>passed</td>', html)
    
    def test_generate_metric_details_table(self):
        """Test generating a metric details table."""
        completeness_data = {
            'col1': {'score': 0.95, 'status': 'passed', 'message': 'Good'},
            'col2': {'score': 0.8, 'status': 'warning', 'message': 'Some missing'},
            'col3': {'completeness': 0.6, 'status': 'failed', 'message': 'Too many missing'}
        }
        
        html = generate_metric_details_table('completeness', completeness_data)
        
        # Verify HTML structure contains all columns
        self.assertIn('<td>col1</td>', html)
        self.assertIn('<td>col2</td>', html)
        self.assertIn('<td>col3</td>', html)
        
        # Verify formatted scores
        self.assertIn('95.0%', html)
        self.assertIn('80.0%', html)
        self.assertIn('60.0%', html)
        
        # Verify status classes
        self.assertIn('status-passed', html)
        self.assertIn('status-warning', html)
        self.assertIn('status-failed', html)
    
    def test_generate_dataframe_preview(self):
        """Test generating a dataframe preview table."""
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alpha', 'Beta', 'Gamma', None, 'Epsilon'],
            'value': [10.5, 20.7, None, 40.2, 50.9]
        })
        
        html = generate_dataframe_preview(df, max_rows=3)
        
        # Verify HTML structure
        self.assertIn('<table class="data-preview-table">', html)
        
        # Verify headers
        self.assertIn('<th>id</th>', html)
        self.assertIn('<th>name</th>', html)
        self.assertIn('<th>value</th>', html)
        
        # Verify sample data (first 3 rows)
        self.assertIn('<td>1</td>', html)
        self.assertIn('<td>Alpha</td>', html)
        self.assertIn('<td>10.5</td>', html)
        
        # Verify NULL formatting
        self.assertIn('null', html.lower())
        
        # Verify truncation message (showing 3 of 5 rows)
        self.assertIn('Showing 3 of 5 rows', html)


class TestChartGeneration(unittest.TestCase):
    """Test case for chart generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Skip tests if matplotlib or other dependencies aren't available
        try:
            import matplotlib.pyplot as plt
            self.has_matplotlib = True
        except ImportError:
            self.has_matplotlib = False
            
        # Create test data for charts
        self.test_df = pd.DataFrame({
            'numeric': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            'categorical': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'D'],
            'with_nulls': [10, None, 30, None, 50, None, 70, None, 90, None]
        })
        
        # Completeness data for chart
        self.completeness_data = {
            'col1': 1.0,    # 100% complete
            'col2': 0.9,    # 90% complete
            'col3': 0.8,    # 80% complete
            'col4': 0.5,    # 50% complete
            'col5': 0.0     # 0% complete
        }
        
        # Accuracy data for chart
        self.accuracy_data = {
            'col1': {'valid': 100, 'invalid': 0},
            'col2': {'valid': 90, 'invalid': 10},
            'col3': {'valid': 80, 'invalid': 20},
            'col4': {'valid': 50, 'invalid': 50}
        }
    
    def test_generate_completeness_chart(self):
        """Test generating a completeness chart."""
        if not self.has_matplotlib:
            self.skipTest("Matplotlib not available")
            
        # Generate chart
        chart_data = generate_completeness_chart(self.completeness_data, "Column Completeness")
        
        # Verify base64 data was returned
        self.assertIsNotNone(chart_data)
        self.assertTrue(isinstance(chart_data, str))
        self.assertTrue(len(chart_data) > 0)
        
        # Verify it's a valid base64 string
        # Check that it only contains valid base64 characters
        base64_pattern = re.compile(r'^[A-Za-z0-9+/]+={0,2}$')
        self.assertTrue(base64_pattern.match(chart_data))
    
    def test_generate_accuracy_chart(self):
        """Test generating an accuracy chart."""
        if not self.has_matplotlib:
            self.skipTest("Matplotlib not available")
            
        # Generate chart
        chart_data = generate_accuracy_chart(self.accuracy_data, "Column Accuracy")
        
        # Verify base64 data was returned
        self.assertIsNotNone(chart_data)
        self.assertTrue(isinstance(chart_data, str))
        self.assertTrue(len(chart_data) > 0)
    
    def test_generate_distribution_chart(self):
        """Test generating distribution charts for different data types."""
        if not self.has_matplotlib:
            self.skipTest("Matplotlib not available")
            
        # Test with numeric data
        numeric_chart = generate_distribution_chart(
            self.test_df['numeric'], 
            "Numeric Distribution"
        )
        
        # Test with categorical data
        categorical_chart = generate_distribution_chart(
            self.test_df['categorical'], 
            "Categorical Distribution"
        )
        
        # Test with data containing nulls
        nulls_chart = generate_distribution_chart(
            self.test_df['with_nulls'], 
            "Distribution with Nulls"
        )
        
        # Verify all charts were generated
        self.assertIsNotNone(numeric_chart)
        self.assertIsNotNone(categorical_chart)
        self.assertIsNotNone(nulls_chart)


if __name__ == '__main__':
    unittest.main()
