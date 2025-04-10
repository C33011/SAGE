"""
Example: Database Quality Assessment with SAGE.

This example demonstrates how to:
1. Connect to an SQLite database (creates a sample one if needed)
2. Apply data quality metrics to assess tables
3. Generate a report on the database quality
"""

import os
import sys
import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, text
import datetime
from pathlib import Path
import logging

# Set up logging to see detailed information from SAGE
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the src directory to the Python path if running without installation
project_dir = Path(__file__).parent.parent
src_dir = project_dir / 'src'
if src_dir.exists():
    sys.path.insert(0, str(src_dir))

from sage.graders.database_grader import DatabaseGrader
from sage.metrics.completeness import CompletenessMetric
from sage.metrics.accuracy import AccuracyMetric
from sage.metrics.consistency import ConsistencyMetric  # Added consistency metric
from sage.metrics.timeliness import TimelinessMetric     # Added timeliness metric
from sage.reports.generator import generate_html_report
from sage.data.profiler import DataProfiler, profile_dataframe  # Added data profiler


def create_sample_database():
    """Create a sample SQLite database with some data quality issues."""
    print("Creating sample database...")
    
    # Create a directory for example data if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Database file path
    db_path = os.path.join(data_dir, 'sample_retail.db')
    
    # Create a connection to the database (this will create the file if it doesn't exist)
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create tables and populate with sample data
    # 1. Products table - with some missing data
    products_data = {
        'product_id': range(1, 21),
        'product_name': [
            'Laptop', 'Smartphone', 'Tablet', 'Monitor', 'Keyboard',
            'Mouse', 'Headphones', None, 'Printer', 'Scanner',  # Added a NULL value to test completeness
            'Webcam', 'Speakers', 'Router', 'Hard Drive', 'SSD',
            'RAM', 'Graphics Card', 'Processor', None, 'Power Supply'  # Another NULL value
        ],
        'category': [
            'Computers', 'Phones', 'Tablets', 'Peripherals', 'Peripherals',
            'Peripherals', 'Audio', 'Audio', 'Peripherals', 'Peripherals',
            'Peripherals', 'Audio', 'Networking', 'Storage', 'Storage',
            'Components', 'Components', 'Components', 'Components', 'Components'
        ],
        'price': [
            1299.99, 899.99, 499.99, 299.99, 89.99,
            49.99, 129.99, 199.99, 249.99, 179.99,
            69.99, 149.99, 89.99, 129.99, 159.99,
            None, 399.99, 349.99, 299.99, None
        ],
        'stock_quantity': [
            15, 30, 25, 20, 50,
            75, 40, 35, 10, 5,
            30, 20, 15, 25, 20,
            40, 15, 10, 8, 12
        ],
        'manufacturer': [
            'TechCorp', 'GadgetWorks', 'TabletMaster', 'ScreenPro', 'TypeMaster',
            'ClickMaster', 'SoundWaves', 'AudioMax', 'PrintPro', 'ScanTech',
            'WebVision', 'SoundBox', 'NetConnect', 'DataStore', 'SpeedDrive',
            'MemoryBoost', 'PixelPower', 'CoreMaster', None, 'PowerSource'  # NULL value in non-crucial field
        ]
    }
    
    products_df = pd.DataFrame(products_data)
    products_df.to_sql('products', engine, index=False, if_exists='replace')
    
    # 2. Customers table - with some invalid data
    customers_data = {
        'customer_id': range(1, 21),
        'first_name': [
            'John', 'Jane', 'Robert', 'Maria', 'James',
            'Patricia', 'Michael', 'Linda', 'William', 'Elizabeth',
            'David', 'Barbara', 'Richard', 'Susan', 'Joseph',
            'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen'
        ],
        'last_name': [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones',
            'Miller', 'Davis', 'Garcia', 'Rodriguez', 'Wilson',
            'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Hernandez',
            'Moore', 'Martin', 'Jackson', 'Thompson', 'White'
        ],
        'email': [
            'john.smith@example.com', 'jane.johnson@example.com', 'robert.williams@example',  # missing domain
            'maria.brown@example.com', 'james.jonesexample.com',  # missing @ symbol
            'patricia.miller@example.com', 'michael.davis@example.com', 'linda.garcia@example.com',
            'william.rodriguez@example.com', 'elizabeth.wilson@example.com',
            'david.martinez@example.com', 'barbara.anderson@example.com', 'richard.taylor@example.com',
            'susan.thomas@example.com', 'joseph.hernandez@example.com',
            'jessica.moore@example.com', 'thomas.martin@example.com', 'sarah.jackson@example.com',
            'charles.thompson@example.com', 'karen.white@example.com'
        ],
        'phone': [
            '555-123-4567', '555-234-5678', '555-345-6789', '555-456-7890', '555-567-8901',
            '555-678-9012', '555-789-0123', '555-890-1234', '555-901-2345', None,
            '555-012-3456', '555-123-4567', None, '555-234-5678', '555-345-6789',
            '555-456-7890', '555-567-8901', '555-678-9012', '555123-4567',
            '555-789-0123'
        ],
        'address': [
            '123 Main St', '456 Elm St', '789 Oak Ave', '101 Pine Rd', '202 Maple Dr',
            '303 Cedar Ln', '404 Birch Ct', '505 Redwood Pl', '606 Spruce Way', '707 Fir Blvd',
            '808 Willow St', '909 Ash Ave', '110 Cherry Rd', '211 Walnut Dr', '312 Hickory Ln',
            None, None, '413 Chestnut Ct', '514 Beech Pl', '615 Poplar Way'
        ],
        'registration_date': [
            '2020-01-15', '2020-02-20', '2020-03-10', '2020-04-05', '2020/05/12',
            '2020-06-18', '2020-07-22', '2020-08-30', '2020-09-05', '2020-10-10',
            '2020-11-15', '2020-12-20', '2021-01-25', '2021-02-28', '2021-03-15',
            '2021-04-10', '2021-05-20', '2021-06-25', '2021-07-30', '07/15/2021'
        ]
    }
    
    customers_df = pd.DataFrame(customers_data)
    customers_df.to_sql('customers', engine, index=False, if_exists='replace')
    
    # 3. Orders table - with some data issues
    orders_data = {
        'order_id': range(1, 31),
        'customer_id': [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            2, 5, 7, 10, 12, 14, 16, 18, None, None
        ],
        'order_date': [
            '2022-01-05', '2022-01-10', '2022-01-15', '2022-01-20', '2022-01-25',
            '2022-02-05', '2022-02-10', '2022-02-15', '2022-02-20', '2022-02-25',
            '2022-03-05', '2022-03-10', '2022-03-15', '2022-03-20', '2022-03-25',
            '2022-04-05', '2022-04-10', '2022-04-15', '2022-04-20', '2022-04-25',
            '2022-05-05', '2022-05-10', '2022-05-15', '2022-05-20', '2022-05-25',
            '2022/06/05', '2022/06/10', '2022/06/15', '2022/06/20', '2022/06/25'
        ],
        'total_amount': [
            299.99, 1499.98, 549.99, 349.99, 89.99,
            1299.99, 179.98, 399.97, 749.98, 229.99,
            499.99, 99.99, 269.98, 459.97, 639.96,
            819.95, 999.94, 1179.93, 1359.92, 1539.91,
            299.99, -50.00,
            549.99, 349.99, 89.99,
            1299.99, 179.98, 399.97, 749.98, 5000000.00
        ],
        'payment_method': [
            'Credit Card', 'PayPal', 'Credit Card', 'Debit Card', 'PayPal',
            'Credit Card', 'Debit Card', 'PayPal', 'Credit Card', 'Debit Card',
            'PayPal', 'Credit Card', 'Debit Card', 'PayPal', 'Credit Card',
            'Debit Card', 'PayPal', 'Credit Card', 'Debit Card', 'PayPal',
            'Credit Card', 'Debit Card', 'PayPal', 'Credit Card', 'Debit Card',
            'Bitcoin',
            'Credit Card', 'Debit Card', 'PayPal', None
        ],
        'status': [
            'Delivered', 'Delivered', 'Delivered', 'Delivered', 'Delivered',
            'Delivered', 'Delivered', 'Delivered', 'Delivered', 'Delivered',
            'Shipped', 'Shipped', 'Shipped', 'Shipped', 'Shipped',
            'Processing', 'Processing', 'Processing', 'Processing', 'Processing',
            'Cancelled', 'Cancelled', 'Cancelled', 'Returned', 'Returned',
            'Delivered', 'Delivered', 'Delivered', 'DeliveredX',
            'Delivered'
        ]
    }
    
    orders_df = pd.DataFrame(orders_data)
    orders_df.to_sql('orders', engine, index=False, if_exists='replace')
    
    # 4. Order Items table - linking orders to products
    order_items_data = {
        'order_item_id': range(1, 41),
        'order_id': [
            1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
            6, 6, 7, 7, 8, 8, 9, 9, 10, 10,
            11, 11, 12, 12, 13, 13, 14, 14, 15, 15,
            16, 16, 17, 17, 18, 18, 19, 19, 20, 20
        ],
        'product_id': [
            1, 5, 2, 7, 3, 8, 4, 9, 5, 10,
            6, 11, 7, 12, 8, 13, 9, 14, 10, 15,
            11, 16, 12, 17, 13, 18, 14, 19, 15, 20,
            16, 1, 17, 2, 18, 3, 19, 4, 20, 5
        ],
        'quantity': [
            1, 2, 1, 1, 1, 1, 1, 1, 1, 2,
            2, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 1, 1, 1, 1, 1, 1, 1, 1, 0,
            1, 2, 1, 1, 1, 1, 1, 1, 1, -1
        ],
        'unit_price': [
            1299.99, 89.99, 899.99, 129.99, 499.99, 199.99, 299.99, 249.99, 89.99, 179.99,
            49.99, 69.99, 129.99, 149.99, 199.99, 89.99, 249.99, 129.99, 179.99, 159.99,
            69.99, 0.00,
            149.99, 399.99, 89.99, 349.99, 129.99, 299.99, 159.99, None,
            None, 1299.99, 399.99, 899.99, 349.99, 499.99, 299.99, 299.99, 299.99, 89.99
        ],
        'discount': [
            0.00, 0.00, 0.00, 0.00, 0.00,
            0.10, 0.10, 0.10, 0.10, 0.10,
            0.15, 0.15, 0.15, 0.15, 0.15,
            0.20, 0.20, 0.20, 0.20, 0.20,
            0.25, 0.25, 0.25, 0.25, 0.25,
            0.30, 0.30, 0.30, 0.30, 0.30,
            0.35, 0.35, 0.35, 0.35, 0.35,
            0.40, 0.40, 0.40, 0.40, 2.00
        ]
    }
    
    order_items_df = pd.DataFrame(order_items_data)
    order_items_df.to_sql('order_items', engine, index=False, if_exists='replace')
    
    print(f"Sample retail database created at: {db_path}")
    return f'sqlite:///{db_path}'


def main():
    """Run the example workflow to grade a database."""
    print("=" * 80)
    print("SAGE Example: Database Quality Assessment")
    print("=" * 80)
    
    # Step 1: Create sample database if needed
    connection_string = create_sample_database()
    
    # Step 2: Set up the grader with metrics
    print("\nSetting up database grader with metrics...")
    grader = DatabaseGrader(name="Retail Database Analysis")
    
    # Add completeness metric
    print("\n- Configuring Completeness Metric")
    completeness = CompletenessMetric(
        warning_threshold=0.9,  # Warn if completeness is below 90%
        failure_threshold=0.7   # Fail if completeness is below 70%
    )
    grader.add_metric("completeness", completeness)
    
    # Add accuracy metric with detailed validation rules
    print("\n- Configuring Accuracy Metric")
    accuracy = AccuracyMetric(
        warning_threshold=0.95,  # Higher threshold for accuracy
        failure_threshold=0.8
    )
    
    # Email pattern validation
    print("  Adding email pattern validation")
    accuracy.add_pattern_check("email", r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    
    # Phone number format validation (simple version)
    print("  Adding phone format validation")
    accuracy.add_pattern_check("phone", r'^\d{3}-\d{3}-\d{4}$')
    
    # Numeric range validations
    print("  Adding numeric range validations")
    accuracy.add_range_check("price", min_value=0.0)
    accuracy.add_range_check("stock_quantity", min_value=0)
    accuracy.add_range_check("total_amount", min_value=0.0, max_value=10000.0)
    accuracy.add_range_check("quantity", min_value=1)
    accuracy.add_range_check("discount", min_value=0.0, max_value=1.0)
    
    # Categorical validations
    print("  Adding categorical validations")
    accuracy.add_categorical_check("payment_method", 
                                  ["Credit Card", "Debit Card", "PayPal", "Bank Transfer", "Cash"])
    
    accuracy.add_categorical_check("status", 
                                  ["Processing", "Shipped", "Delivered", "Cancelled", "Returned"])
    
    grader.add_metric("accuracy", accuracy)
    
    # Add consistency metric with relationship checks
    print("\n- Configuring Consistency Metric")
    consistency = ConsistencyMetric(
        warning_threshold=0.95,
        failure_threshold=0.8
    )
    
    # Add relationship checks - updating these to work with the sample data
    print("  Adding relationship checks")
    
    # Check that orders link to valid customers
    consistency.add_relationship_check(
        name="order_customer",
        condition="customer_id.notnull()",
        implies="customer_id >= 1"  # Simple check to ensure IDs are valid
    )
    
    # Check that order totals match order item totals
    # This won't work directly without JOINs, but demonstrates the concept
    consistency.add_relationship_check(
        name="status_valid",
        condition="status.notnull()",
        implies="status.isin(['Processing', 'Shipped', 'Delivered', 'Cancelled', 'Returned'])"
    )
    
    # For order_items table
    consistency.add_relationship_check(
        name="valid_quantities",
        condition="quantity.notnull()",
        implies="quantity > 0"
    )
    
    grader.add_metric("consistency", consistency)
    
    # Update Timeliness Metric for realistic date ranges in our sample data
    print("\n- Configuring Timeliness Metric")
    
    # Use a reference date that works with our sample data
    # The sample data has dates from 2020-2022, so set reference date accordingly
    reference_date = datetime.datetime.strptime('2023-01-01', '%Y-%m-%d').date()
    print(f"  Using reference date: {reference_date}")
    
    timeliness = TimelinessMetric(
        reference_date=reference_date,  # Set to a date after our sample data
        warning_threshold=0.9,
        failure_threshold=0.7
    )
    
    # Update the age checks to be more appropriate for our sample data
    print("  Adding age checks")
    timeliness.add_age_check(
        column="registration_date",
        max_age=1095,  # 3 years in days
        warning_threshold=730  # 2 years in days
    )
    
    # Update the freshness checks for our sample data dates
    print("  Adding freshness checks")
    timeliness.add_freshness_check(
        column="order_date",
        max_age=365,  # Data within the last year from reference date
        warning_threshold=180  # Warning if older than 6 months from reference date
    )
    
    grader.add_metric("timeliness", timeliness)
    
    # Step 3: Connect to the database
    print(f"\nConnecting to database: {connection_string}")
    try:
        engine = create_engine(connection_string)
        grader.connect(engine)
        print("✓ Connection successful")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return
    
    # Print available tables
    tables = grader.get_available_tables()
    print(f"\nAvailable tables: {tables}")
    
    # Step 4: Analyze each table
    all_results = {}
    table_profiles = {}
    
    # Update how the today variable is passed for consistency checks
    # when we grade each table
    for table in tables:
        print(f"\n{'='*40}")
        print(f"Analyzing table: {table}")
        print(f"{'='*40}")
        
        grader.set_active_table(table)
        
        # Get table information and sample data
        table_info = grader.get_table_info()
        print(f"\nTable Structure:")
        print(f"  Columns: {len(table_info['columns'])} ({', '.join(table_info['columns'].keys())})")
        print(f"  Rows: {table_info['row_count']}")
        
        # Get data sample for profiling
        try:
            sample_query = f"SELECT * FROM {table} LIMIT 1000"
            sample_data = pd.read_sql(sample_query, engine)
            
            print(f"\nData Sample Preview (first 5 rows):")
            print(sample_data.head().to_string())
            
            # Profile the data
            print(f"\nProfiling data...")
            profile = profile_dataframe(sample_data)
            table_profiles[table] = profile
            
            # Show some key profiling statistics
            missing_cells = profile['overall_stats']['missing_cells']
            total_cells = table_info['column_count'] * min(1000, table_info['row_count'])
            missing_percent = (missing_cells / total_cells) * 100 if total_cells > 0 else 0
            
            print(f"  Missing data: {missing_cells} cells ({missing_percent:.2f}%)")
            
            if 'duplicate_rows' in profile['overall_stats']:
                duplicates = profile['overall_stats']['duplicate_rows']
                duplicate_percent = (duplicates / len(sample_data)) * 100 if len(sample_data) > 0 else 0
                print(f"  Duplicate rows: {duplicates} ({duplicate_percent:.2f}%)")
            
            # Show column-specific issues
            print("\nColumn-level data quality observations:")
            for col, col_profile in profile['column_profiles'].items():
                issues = []
                
                # Check for missing data
                if col_profile.get('missing_percent', 0) > 0.05:
                    issues.append(f"{col_profile['missing_percent']:.1%} missing values")
                
                # Check for high cardinality in categorical columns
                if col_profile.get('is_categorical', False) and col_profile.get('unique_percent', 0) > 0.8:
                    issues.append(f"High cardinality ({col_profile['unique_count']} unique values)")
                
                # Check for potential outliers in numeric columns
                if col_profile.get('is_numeric', False) and 'std' in col_profile and col_profile['std'] is not None:
                    skewness = col_profile.get('skewness')
                    if skewness is not None and abs(skewness) > 3:
                        issues.append(f"Highly skewed data (skew={skewness:.2f})")
                
                if issues:
                    print(f"  - {col}: {', '.join(issues)}")
        
        except Exception as e:
            print(f"Error profiling data: {e}")
        
        # Grade the data with all metrics
        print(f"\nGrading table with all metrics...")
        
        # Instead of using query_params, we need to inject the date values directly
        # Convert registration_date and order_date to datetime if they exist in the table
        try:
            sample_query = f"SELECT * FROM {table} LIMIT 1"
            sample_data = pd.read_sql(sample_query, engine)
            
            # Fix date formats to ensure consistent YYYY-MM-DD format
            # This is a common data quality issue in real databases
            if 'registration_date' in sample_data.columns:
                # Convert MM/DD/YYYY format to YYYY-MM-DD
                date_fix_query = f"""
                UPDATE {table} 
                SET registration_date = substr(registration_date, 7, 4) || '-' || 
                                       substr(registration_date, 1, 2) || '-' || 
                                       substr(registration_date, 4, 2)
                WHERE registration_date LIKE '%/%'
                """
                try:
                    with engine.connect() as conn:
                        conn.execute(text(date_fix_query))
                        conn.commit()
                    print(f"  Fixed date formats in {table}.registration_date")
                except Exception as e:
                    print(f"  Could not fix date formats: {str(e)}")
            
            if 'order_date' in sample_data.columns:
                # Update order_date format in database if needed
                date_fix_query = f"""
                UPDATE {table} 
                SET order_date = substr(order_date, 7, 4) || '-' || 
                                 substr(order_date, 1, 2) || '-' || 
                                 substr(order_date, 4, 2)
                WHERE order_date LIKE '%/%'
                """
                try:
                    with engine.connect() as conn:
                        conn.execute(text(date_fix_query))
                        conn.commit()
                    print(f"  Fixed date formats in {table}.order_date")
                except Exception as e:
                    print(f"  Could not fix date formats: {str(e)}")
                    
        except Exception as e:
            print(f"  Could not prepare date fields: {str(e)}")
        
        # For consistency with "today" value, we'll set up a global SQL variable if possible
        try:
            today_query = f"PRAGMA user_version = '{reference_date.isoformat()}';"
            with engine.connect() as conn:
                conn.execute(text(today_query))
                conn.commit()
        except Exception as e:
            print(f"  Note: Could not set reference date in database: {str(e)}")
        
        # Now grade the table without query_params
        table_results = grader.grade()
        all_results[table] = table_results
        
        # Display results for each metric
        print("\nMetric Results:")
        for metric_name, metric_result in table_results.get('metrics', {}).items():
            score = metric_result.get('score', 0) * 100
            status = metric_result.get('status', 'unknown')
            message = metric_result.get('message', 'No message provided')
            
            # Format the status with a color indicator
            status_symbol = "✓" if status == "passed" else "⚠" if status == "warning" else "✗"
            
            print(f"  {metric_name}: {score:.1f}% - {status_symbol} {status.upper()} - {message}")
            
            # Show detailed information for each metric
            if metric_name == "completeness" and 'columns' in metric_result:
                print("    Column completeness:")
                for col, col_result in metric_result['columns'].items():
                    if col_result['completeness'] < 1.0:
                        col_score = col_result['completeness'] * 100
                        col_missing = col_result.get('missing_count', 0)
                        print(f"      - {col}: {col_score:.1f}% complete ({col_missing} missing values)")
            
            elif metric_name == "accuracy" and 'details' in metric_result:
                print("    Accuracy issues:")
                for col, col_result in metric_result['details'].items():
                    if col_result.get('invalid', 0) > 0:
                        valid = col_result.get('valid', 0)
                        invalid = col_result.get('invalid', 0)
                        message = col_result.get('message', '')
                        print(f"      - {col}: {invalid} invalid values out of {valid + invalid} - {message}")
            
            elif metric_name == "consistency" and 'rules' in metric_result:
                print("    Consistency rule results:")
                for rule_name, rule_result in metric_result['rules'].items():
                    consistent = rule_result.get('consistent_rows', 0)
                    inconsistent = rule_result.get('inconsistent_rows', 0)
                    if inconsistent > 0:
                        print(f"      - {rule_name}: {inconsistent} inconsistent rows out of {consistent + inconsistent}")
                        # Show examples if available
                        if 'examples' in rule_result and rule_result['examples']:
                            print(f"        Example: {rule_result['examples'][0]}")
            
            elif metric_name == "timeliness" and 'details' in metric_result:
                print("    Timeliness issues:")
                for col, col_result in metric_result['details'].items():
                    timely = col_result.get('timely', 0)
                    untimely = col_result.get('untimely', 0)
                    if untimely > 0:
                        check_type = col_result.get('check_type', 'check')
                        print(f"      - {col} ({check_type}): {untimely} untimely values out of {timely + untimely}")
    
    # Step 5: Create a comprehensive report with all the collected data
    print("\n" + "="*40)
    print("Creating comprehensive quality report...")
    print("="*40)
    
    # Initialize consolidated metrics
    consolidated_metrics = {
        "completeness": {
            "score": 0.0,
            "status": "passed",
            "tables": {}
        },
        "accuracy": {
            "score": 0.0,
            "status": "passed",
            "tables": {}
        },
        "consistency": {
            "score": 0.0,
            "status": "passed",
            "tables": {}
        },
        "timeliness": {
            "score": 0.0,
            "status": "passed",
            "tables": {}
        }
    }
    
    # Collect metrics across all tables
    tables_with_metrics = {metric: 0 for metric in consolidated_metrics}
    
    for table, results in all_results.items():
        metrics = results.get('metrics', {})
        
        for metric_name in consolidated_metrics:
            if metric_name in metrics:
                tables_with_metrics[metric_name] += 1
                table_score = metrics[metric_name]['score']
                table_status = metrics[metric_name]['status']
                consolidated_metrics[metric_name]['tables'][table] = {
                    "score": table_score,
                    "status": table_status
                }
                consolidated_metrics[metric_name]['score'] += table_score
    
    # Calculate average scores
    for metric_name, tables_count in tables_with_metrics.items():
        if tables_count > 0:
            consolidated_metrics[metric_name]['score'] /= tables_count
    
    # Determine overall status for each metric
    for metric_name, metric_data in consolidated_metrics.items():
        score = metric_data['score']
        if score < 0.7:
            metric_data['status'] = "failed"
        elif score < 0.9:
            metric_data['status'] = "warning"
        else:
            metric_data['status'] = "passed"
    
    # Calculate overall data quality score
    metrics_count = 0
    overall_score = 0.0
    
    for metric_name, metric_data in consolidated_metrics.items():
        if 'score' in metric_data and tables_with_metrics[metric_name] > 0:
            metrics_count += 1
            overall_score += metric_data['score']
    
    if metrics_count > 0:
        overall_score /= metrics_count
    
    # Determine overall status
    overall_status = "failed"
    if overall_score >= 0.9:
        overall_status = "passed"
    elif overall_score >= 0.7:
        overall_status = "warning"
    
    # Create recommendations based on findings
    recommendations = []
    
    # Completeness recommendations
    if consolidated_metrics['completeness']['score'] < 0.95:
        tables_with_issues = [
            table for table, data in consolidated_metrics['completeness']['tables'].items()
            if data['score'] < 0.95
        ]
        
        if tables_with_issues:
            steps = [
                "Identify columns with missing values",
                "Add NOT NULL constraints for required fields",
                "Implement validation in application code",
                "Review data collection processes"
            ]
            
            # Add specific column recommendations based on profiling
            problematic_columns = []
            for table in tables_with_issues:
                for metric in all_results[table].get('metrics', {}).values():
                    if 'columns' in metric:
                        for col, details in metric['columns'].items():
                            if details.get('completeness', 1.0) < 0.9:
                                problematic_columns.append(f"{table}.{col}")
            
            if problematic_columns:
                steps.append(f"Focus on problematic columns: {', '.join(problematic_columns[:5])}" + 
                            (f" and {len(problematic_columns) - 5} others" if len(problematic_columns) > 5 else ""))
            
            recommendations.append({
                "title": "Address Missing Data",
                "priority": "high" if consolidated_metrics['completeness']['score'] < 0.8 else "medium",
                "description": f"Missing data detected in tables: {', '.join(tables_with_issues)}",
                "steps": steps
            })
    
    # Accuracy recommendations
    if consolidated_metrics['accuracy']['score'] < 0.95:
        tables_with_issues = [
            table for table, data in consolidated_metrics['accuracy']['tables'].items()
            if data['score'] < 0.95
        ]
        
        if tables_with_issues:
            # Collect specific accuracy issues
            accuracy_issues = []
            for table in tables_with_issues:
                if 'accuracy' in all_results[table].get('metrics', {}):
                    details = all_results[table]['metrics']['accuracy'].get('details', {})
                    for col, col_details in details.items():
                        if col_details.get('invalid', 0) > 0:
                            accuracy_issues.append(f"{table}.{col}: {col_details.get('message', '')}")
            
            steps = [
                "Review data validation rules",
                "Add CHECK constraints to prevent invalid data",
                "Implement data type constraints",
                "Consider adding triggers for complex validation"
            ]
            
            if accuracy_issues:
                steps.append("Address specific issues:")
                for issue in accuracy_issues[:3]:  # Add top 3 issues
                    steps.append(f"  - {issue}")
                if len(accuracy_issues) > 3:
                    steps.append(f"  - Plus {len(accuracy_issues) - 3} more issues")
            
            priority = "high" if consolidated_metrics['accuracy']['score'] < 0.85 else "medium"
            print(f"Adding accuracy recommendation with {priority} priority")
            
            recommendations.append({
                "title": "Fix Data Accuracy Issues",
                "priority": priority,
                "description": f"Data accuracy issues detected in tables: {', '.join(tables_with_issues)}",
                "steps": steps
            })
    
    # Consistency recommendations
    if 'consistency' in consolidated_metrics and consolidated_metrics['consistency']['score'] < 0.95:
        tables_with_issues = [
            table for table, data in consolidated_metrics['consistency']['tables'].items()
            if data['score'] < 0.95
        ]
        
        if tables_with_issues:
            recommendations.append({
                "title": "Improve Data Consistency",
                "priority": "high" if consolidated_metrics['consistency']['score'] < 0.8 else "medium",
                "description": f"Data consistency issues detected in tables: {', '.join(tables_with_issues)}",
                "steps": [
                    "Review relationship constraints between tables",
                    "Ensure referential integrity with proper foreign keys",
                    "Add business rule validations to maintain data consistency",
                    "Implement application-level validation for complex rules"
                ]
            })
    
    # Timeliness recommendations
    if 'timeliness' in consolidated_metrics and consolidated_metrics['timeliness']['score'] < 0.9:
        tables_with_issues = [
            table for table, data in consolidated_metrics['timeliness']['tables'].items()
            if data['score'] < 0.9
        ]
        
        if tables_with_issues:
            recommendations.append({
                "title": "Address Data Freshness Issues",
                "priority": "medium",
                "description": f"Data timeliness issues detected in tables: {', '.join(tables_with_issues)}",
                "steps": [
                    "Review update frequency of critical data",
                    "Implement data refresh processes for stale data",
                    "Add auditing mechanisms to track data age",
                    "Consider data archiving strategy for old records"
                ]
            })
    
    # Add database-specific recommendations from profiling insights
    unique_constraints_needed = False
    indexing_needed = False
    data_type_issues = False
    
    for table, profile in table_profiles.items():
        # Check for potential duplicate records
        if profile['overall_stats'].get('duplicate_rows', 0) > 0:
            unique_constraints_needed = True
        
        # Check for data type issues
        for col, col_profile in profile['column_profiles'].items():
            if col_profile.get('is_numeric', False) and col_profile.get('dtype', '').startswith('object'):
                data_type_issues = True
                break
    
    if unique_constraints_needed:
        recommendations.append({
            "title": "Add Unique Constraints",
            "priority": "high",
            "description": "Potential duplicate records detected in the database",
            "steps": [
                "Identify natural keys in each table",
                "Add UNIQUE constraints or indices",
                "De-duplicate existing data",
                "Implement application-level duplicate detection"
            ]
        })
    
    # Always add indexing recommendation as it's generally beneficial
    recommendations.append({
        "title": "Review Database Indexing",
        "priority": "medium",
        "description": "Ensure appropriate indexes exist for query performance",
        "steps": [
            "Create indexes on frequently queried columns",
            "Add indexes on foreign key columns",
            "Consider composite indexes for multi-column queries",
            "Review execution plans for slow queries"
        ]
    })
    
    if data_type_issues:
        recommendations.append({
            "title": "Standardize Data Types",
            "priority": "medium",
            "description": "Inconsistent data types detected across columns",
            "steps": [
                "Review column data types for consistency",
                "Convert string representations to proper numeric/date types",
                "Add CHECK constraints for format validation",
                "Document data type standards for future development"
            ]
        })
    
    # Prepare the final report data with detailed insights
    report_data = {
        "title": "Retail Database Quality Assessment",
        "description": f"Comprehensive analysis of {len(tables)} tables in the retail database",
        "overall_score": overall_score,
        "overall_status": overall_status,
        "metrics": consolidated_metrics,
        "tables": {
            table: {
                "info": {
                    "row_count": all_results[table].get("table_info", {}).get("row_count", 0),
                    "column_count": all_results[table].get("table_info", {}).get("column_count", 0),
                    "columns": list(all_results[table].get("table_info", {}).get("columns", {}).keys())
                },
                "metrics": all_results[table].get("metrics", {}),
                "profile": table_profiles.get(table, {})
            } for table in tables
        },
        "details": {
            "database_type": "SQLite",
            "tables_analyzed": len(tables),
            "table_names": tables,
            "total_rows": sum(all_results[table].get("table_info", {}).get("row_count", 0) for table in tables),
            "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_duration": "n/a"  # Could add timing if desired
        },
        "recommendations": recommendations
    }
    
    # Generate HTML report
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(output_dir, f"database_quality_report_{timestamp}.html")
    
    generate_html_report(report_data, report_path)
    
    print("\nDone!")
    print(f"Database quality report generated at: {report_path}")
    print("\nOpen this file in your web browser to view the report.")


if __name__ == "__main__":
    main()
