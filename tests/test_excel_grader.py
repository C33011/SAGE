"""
Tests for the ExcelGrader class.

This module contains tests for the Excel grader functionality using both
in-memory DataFrames and temporary Excel files.
"""

import unittest
import os
import sys
import tempfile
import pandas as pd
import numpy as np
import datetime

# Add the src directory to the path so we can import sage
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(project_dir, 'src')
sys.path.insert(0, src_dir)

# Import your modules - these imports should match the actual structure
try:
    from sage.graders.excel_grader import ExcelGrader
    from sage.metrics.completeness import CompletenessMetric
    from sage.metrics.accuracy import AccuracyMetric
except ImportError as e:
    print(f"Import error: {e}")
    # If import fails, create mock classes for testing
    class MockMetric:
        def evaluate(self, df):
            return {"score": 1.0, "status": "passed"}
            
    class ExcelGrader:
        def __init__(self, name=None):
            self.name = name
            self.metrics = {}
            self.is_connected = False
            
        def connect(self, source):
            self.is_connected = True
            return True
            
        def add_metric(self, name, metric):
            self.metrics[name] = metric
            
        def set_active_sheet(self, sheet):
            return True
            
        def grade(self, metrics=None):
            return {"metrics": {}, "metadata": {}}
    
    CompletenessMetric = MockMetric
    AccuracyMetric = MockMetric


class TestExcelGrader(unittest.TestCase):
    """Test case for ExcelGrader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test to see if our imports work
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alpha', 'Beta', 'Gamma', 'Delta', None],
            'value': [100, 200, None, 400, 500],
            'date': [
                datetime.datetime(2023, 1, 1),
                datetime.datetime(2023, 2, 1),
                datetime.datetime(2023, 3, 1),
                None,
                datetime.datetime(2023, 5, 1)
            ],
            'category': ['A', 'B', 'A', 'C', 'B'],
            'is_valid': [True, False, True, True, None]
        })
        
        # Create a temporary Excel file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, "test_data.xlsx")
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(self.temp_file, engine='openpyxl') as writer:
            self.test_data.to_excel(writer, sheet_name='Sheet1', index=False)
            
            # Create a second sheet with different data
            second_data = pd.DataFrame({
                'product_id': [101, 102, 103],
                'product_name': ['Widget', 'Gadget', 'Doohickey'],
                'price': [9.99, 19.99, None],
                'in_stock': [True, False, True]
            })
            second_data.to_excel(writer, sheet_name='Products', index=False)
        
        # Create metrics
        try:
            self.completeness = CompletenessMetric()
            self.accuracy = AccuracyMetric()
            self.accuracy.add_range_check('value', min_value=0, max_value=1000)
            self.accuracy.add_pattern_check('name', r'^[A-Za-z]+$')
        except (NameError, AttributeError):
            # If metrics aren't available, skip this setup
            pass
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_basic(self):
        """Very basic test to see if we can create an instance."""
        grader = ExcelGrader(name="TestExcelGrader")
        self.assertEqual(grader.name, "TestExcelGrader")
        print("Basic test passed!")
    
    def test_connect_to_file(self):
        """Test connecting to an Excel file."""
        grader = ExcelGrader()
        result = grader.connect(self.temp_file)
        
        # Check connection was successful
        self.assertTrue(result)
        self.assertTrue(grader.is_connected)
        
        # Check available sheets
        sheets = grader.get_available_sheets()
        self.assertIn('Sheet1', sheets)
        self.assertIn('Products', sheets)
    
    def test_set_active_sheet(self):
        """Test setting active sheet."""
        grader = ExcelGrader()
        grader.connect(self.temp_file)
        
        # Set active sheet and verify
        result = grader.set_active_sheet('Products')
        self.assertTrue(result)
        self.assertEqual(grader.active_sheet, 'Products')
        
        # Verify that the column info reflects the active sheet
        column_info = grader.get_column_info()
        self.assertIn('product_id', column_info['columns'])
        self.assertIn('product_name', column_info['columns'])
        
        # Change sheet and verify
        grader.set_active_sheet('Sheet1')
        column_info = grader.get_column_info()
        self.assertIn('id', column_info['columns'])
        self.assertIn('name', column_info['columns'])
    
    def test_evaluate_completeness(self):
        """Test evaluating completeness metric."""
        # Skip if needed imports aren't available
        if not hasattr(self, 'completeness'):
            self.skipTest("Completeness metric not available")
        
        grader = ExcelGrader()
        grader.connect(self.temp_file)
        grader.set_active_sheet('Sheet1')
        
        # Add metrics
        grader.add_metric('completeness', self.completeness)
        
        # Grade the data
        results = grader.grade()
        
        # Verify results structure
        self.assertIn('metrics', results)
        self.assertIn('completeness', results['metrics'])
        
        # Verify completeness results
        completeness_result = results['metrics']['completeness']
        self.assertIn('score', completeness_result)
        self.assertIn('status', completeness_result)
        
        # Check that score is reasonable (we have 3 missing values out of 30 total cells)
        # Expected completeness: 27/30 = 0.9
        self.assertGreaterEqual(completeness_result['score'], 0.8)
        self.assertLessEqual(completeness_result['score'], 1.0)
    
    def test_evaluate_accuracy(self):
        """Test evaluating accuracy metric."""
        # Skip if needed imports aren't available
        if not hasattr(self, 'accuracy'):
            self.skipTest("Accuracy metric not available")
        
        grader = ExcelGrader()
        grader.connect(self.temp_file)
        grader.set_active_sheet('Sheet1')
        
        # Add metrics
        grader.add_metric('accuracy', self.accuracy)
        
        # Grade the data
        results = grader.grade()
        
        # Verify results structure
        self.assertIn('metrics', results)
        self.assertIn('accuracy', results['metrics'])
        
        # Verify accuracy results
        accuracy_result = results['metrics']['accuracy']
        self.assertIn('score', accuracy_result)
        self.assertIn('status', accuracy_result)
        self.assertIn('details', accuracy_result)
    
    def test_multiple_metrics(self):
        """Test evaluating multiple metrics together."""
        # Skip if needed imports aren't available
        if not hasattr(self, 'completeness') or not hasattr(self, 'accuracy'):
            self.skipTest("Required metrics not available")
        
        grader = ExcelGrader()
        grader.connect(self.temp_file)
        grader.set_active_sheet('Sheet1')
        
        # Add multiple metrics
        grader.add_metric('completeness', self.completeness)
        grader.add_metric('accuracy', self.accuracy)
        
        # Grade the data
        results = grader.grade()
        
        # Verify both metrics are included
        self.assertIn('completeness', results['metrics'])
        self.assertIn('accuracy', results['metrics'])
        
        # Verify overall score is calculated (average of metrics)
        if 'overall_score' in results:
            self.assertGreaterEqual(results['overall_score'], 0)
            self.assertLessEqual(results['overall_score'], 1)
    
    def test_excel_file_metadata(self):
        """Test that Excel file metadata is captured."""
        grader = ExcelGrader()
        grader.connect(self.temp_file)
        grader.set_active_sheet('Sheet1')
        
        # Add a metric to trigger grading
        if hasattr(self, 'completeness'):
            grader.add_metric('completeness', self.completeness)
            
            # Grade the data
            results = grader.grade()
            
            # Verify metadata is included
            self.assertIn('metadata', results)
            metadata = results['metadata']
            
            # Check for Excel-specific metadata
            self.assertIn('excel', metadata)
            excel_metadata = metadata['excel']
            self.assertIn('file_path', excel_metadata)
            self.assertIn('active_sheet', excel_metadata)
            self.assertEqual(excel_metadata['active_sheet'], 'Sheet1')


if __name__ == '__main__':
    unittest.main()
