"""
Tests for the data profiling functionality.

This module tests the data profiling capabilities, including generating
statistics, visualizations, and data insights.
"""

import unittest
import os
import sys
import pandas as pd
import numpy as np
import datetime
import tempfile

# Add the src directory to the path so we can import sage
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(project_dir, 'src')
sys.path.insert(0, src_dir)

# Try to import data profiler
try:
    from sage.data.profiler import DataProfiler, profile_dataframe
    PROFILER_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    PROFILER_AVAILABLE = False


class TestDataProfiler(unittest.TestCase):
    """Test case for DataProfiler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PROFILER_AVAILABLE:
            self.skipTest("DataProfiler not available")
            
        # Create a diverse test dataset
        self.test_data = pd.DataFrame({
            # Numeric columns
            'id': range(1, 101),
            'int_with_nulls': [i if i % 10 != 0 else None for i in range(1, 101)],
            'float_values': [float(i) / 10 for i in range(1, 101)],
            
            # Date columns
            'dates': pd.date_range(start='2023-01-01', periods=100, freq='D'),
            
            # Categorical/Text columns
            'category': np.random.choice(['A', 'B', 'C', 'D'], 100),
            'text': ['Text ' + str(i) for i in range(1, 101)],
            'text_with_nulls': [f'Text {i}' if i % 5 != 0 else None for i in range(1, 101)],
            
            # Boolean column
            'boolean': np.random.choice([True, False], 100),
            
            # Mixed content
            'mixed': [str(i) if i % 3 == 0 else (i if i % 3 == 1 else None) for i in range(1, 101)]
        })
        
        # Create profiler instance
        self.profiler = DataProfiler(self.test_data)
    
    def test_overall_statistics(self):
        """Test overall dataset statistics."""
        stats = self.profiler.get_overall_stats()
        
        # Verify basic statistics
        self.assertEqual(stats['row_count'], 100)
        self.assertEqual(stats['column_count'], 9)
        
        # Verify missing values calculation
        # Expected missing: 10 (int_with_nulls) + 20 (text_with_nulls) + ~33 (mixed) = ~63
        self.assertGreaterEqual(stats['missing_cells'], 60)
        self.assertLessEqual(stats['missing_cells'], 65)
        
        # Verify column names
        for col in self.test_data.columns:
            self.assertIn(col, stats['column_names'])
    
    def test_column_profiles(self):
        """Test column-level profile statistics."""
        # Get profile for integer column
        int_profile = self.profiler.get_column_profile('id')
        
        self.assertEqual(int_profile['dtype'], 'int64')
        self.assertEqual(int_profile['missing_count'], 0)
        self.assertEqual(int_profile['unique_count'], 100)
        self.assertEqual(int_profile['is_numeric'], True)
        self.assertEqual(int_profile['min'], 1)
        self.assertEqual(int_profile['max'], 100)
        
        # Get profile for column with nulls
        nulls_profile = self.profiler.get_column_profile('int_with_nulls')
        
        self.assertEqual(nulls_profile['missing_count'], 10)
        self.assertAlmostEqual(nulls_profile['missing_percent'], 0.1, places=2)
        
        # Get profile for categorical column
        cat_profile = self.profiler.get_column_profile('category')
        
        self.assertEqual(cat_profile['is_numeric'], False)
        self.assertLessEqual(cat_profile['unique_count'], 4)  # A, B, C, D
    
    def test_visualizations(self):
        """Test visualization generation."""
        # Get profile for a column that should have visualizations
        profile = self.profiler.get_column_profile('float_values')
        
        # Skip if matplotlib isn't available
        if not hasattr(profile, 'distribution_chart'):
            self.skipTest("Visualization not available")
            
        # Check visualization is generated
        self.assertIn('distribution_chart', profile)
        self.assertTrue(isinstance(profile['distribution_chart'], str))
    
    def test_complete_profile_report(self):
        """Test generating a complete profile report."""
        report = self.profiler.generate_profile_report()
        
        # Verify report structure
        self.assertIn('overall_stats', report)
        self.assertIn('column_profiles', report)
        
        # Verify all columns are profiled
        for col in self.test_data.columns:
            self.assertIn(col, report['column_profiles'])
    
    def test_profile_dataframe_function(self):
        """Test the convenience function for profiling."""
        # Create a small test dataset
        small_df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': ['x', 'y', 'z']
        })
        
        # Profile the dataframe
        profile = profile_dataframe(small_df)
        
        # Verify basic results
        self.assertEqual(profile['overall_stats']['row_count'], 3)
        self.assertEqual(profile['overall_stats']['column_count'], 2)
        self.assertEqual(profile['overall_stats']['missing_cells'], 0)
        
        # Verify column profiles
        self.assertIn('a', profile['column_profiles'])
        self.assertIn('b', profile['column_profiles'])


if __name__ == '__main__':
    unittest.main()
