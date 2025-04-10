"""
Excel File Quality Assessment

This script demonstrates how to use SAGE to analyze the quality of data in an Excel file.
It shows how to apply metrics to check for common data quality issues.
"""

import os
import sys
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

# Add the src directory to the Python path if running without installation
project_dir = Path(__file__).parent.parent
src_dir = project_dir / 'src'
if src_dir.exists():
    sys.path.insert(0, str(src_dir))

from sage.graders.excel_grader import ExcelGrader
from sage.metrics.completeness import CompletenessMetric
from sage.metrics.accuracy import AccuracyMetric
from sage.reports.generator import generate_html_report

def select_file_dialog():
    """Open a file dialog to select an Excel file, with improved error handling."""
    print("Attempting to open file dialog...")
    
    # Method 1: Try to use tkinter file dialog (most reliable)
    try:
        print("Trying tkinter dialog...")
        import tkinter as tk
        from tkinter import filedialog
        
        # Create and immediately withdraw a root window
        root = tk.Tk()
        root.withdraw()
        
        # Ensure window gets focus (helps on some systems)
        root.update()
        
        # Show file dialog and return selected path
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        print(f"Tkinter dialog result: {'Selected file' if file_path else 'No file selected'}")
        if file_path:
            return file_path
    except Exception as e:
        print(f"Tkinter dialog failed: {e}")
    
    # Method 2: Simpler approach for Windows - use system dialog directly
    if sys.platform.startswith('win'):
        try:
            print("Trying Windows API dialog...")
            import subprocess
            
            # Use PowerShell to show the Windows file picker
            ps_script = '''
            Add-Type -AssemblyName System.Windows.Forms
            $dialog = New-Object System.Windows.Forms.OpenFileDialog
            $dialog.Filter = "Excel Files (*.xlsx, *.xls)|*.xlsx;*.xls|All Files (*.*)|*.*"
            $dialog.Title = "Select Excel File"
            $dialog.ShowHelp = $false
            $dialog.ShowDialog() | Out-Null
            Write-Output $dialog.FileName
            '''
            
            # Execute PowerShell script
            result = subprocess.run(
                ["powershell", "-Command", ps_script], 
                capture_output=True, 
                text=True
            )
            
            file_path = result.stdout.strip()
            print(f"Windows dialog result: {'Selected file' if file_path else 'No file selected'}")
            if file_path and os.path.exists(file_path):
                return file_path
        except Exception as e:
            print(f"Windows dialog failed: {e}")
            
    # Fallback to manual input
    print("All file dialog methods failed. Please enter the path manually.")
    return None

def main():
    """
    Main function to demonstrate grading an Excel file.
    """
    print("=" * 80)
    print("SAGE Example: Excel File Quality Assessment")
    print("=" * 80)
    
    # Check if a file path was provided as command line argument
    if len(sys.argv) > 1 and sys.argv[1] and sys.argv[1] != '""' and sys.argv[1] != "''":
        file_path = sys.argv[1].strip('"\'')
    else:
        # No file path provided, or empty quotes - look for default or show dialog
        default_path = os.path.join(os.path.dirname(__file__), 'data', 'sales_data.xlsx')
        
        if os.path.exists(default_path):
            print(f"Default example file found: {default_path}")
            user_input = input(f"Enter path to Excel file, empty for dialog, or press Enter to use example file: ")
            
            if user_input.strip() in ('', '""', "''"):
                # Show file selection dialog
                selected_path = select_file_dialog()
                if selected_path:
                    file_path = selected_path
                else:
                    # Dialog was cancelled or failed, use default
                    print("Using default example file.")
                    file_path = default_path
            else:
                file_path = user_input.strip().strip('"\'')
        else:
            # No default file, first try dialog
            print("No default example file found. Opening file selection dialog...")
            selected_path = select_file_dialog()
            
            if selected_path:
                file_path = selected_path
            else:
                # Dialog was cancelled or failed, ask for manual input
                file_path = input("Enter path to Excel file: ")
                while not os.path.exists(file_path) or not file_path.endswith(('.xlsx', '.xls')):
                    if file_path.lower() in ('q', 'quit', 'exit'):
                        print("Exiting program.")
                        return
                    print("Invalid file path. Please enter a valid Excel file path (or 'q' to quit).")
                    file_path = input("Enter path to Excel file: ")
    
    print(f"\nAnalyzing Excel file: {file_path}")
    
    # Initialize the Excel grader
    grader = ExcelGrader(name="Excel Data Quality Assessment")
    
    # Connect to the Excel file
    try:
        grader.connect(file_path)
        print("Successfully connected to Excel file")
    except Exception as e:
        print(f"Error connecting to Excel file: {e}")
        return
    
    # Get available sheets
    sheets = grader.get_available_sheets()
    print(f"Available sheets: {', '.join(sheets)}")
    
    # Let user select a sheet
    if len(sheets) > 1:
        print("\nSelect a sheet to analyze:")
        for i, sheet in enumerate(sheets, 1):
            print(f"{i}. {sheet}")
        
        sheet_choice = 0
        while sheet_choice < 1 or sheet_choice > len(sheets):
            try:
                sheet_choice = int(input(f"Enter sheet number (1-{len(sheets)}): "))
            except ValueError:
                print("Please enter a valid number")
        
        active_sheet = sheets[sheet_choice - 1]
    else:
        active_sheet = sheets[0]
    
    # Set the active sheet
    grader.set_active_sheet(active_sheet)
    print(f"\nAnalyzing sheet: {active_sheet}")
    
    # Get basic info about the sheet
    try:
        column_info = grader.get_column_info()
        print(f"Rows: {column_info['row_count']}")
        print(f"Columns: {column_info['column_count']}")
        print("Column names: " + ", ".join(column_info['columns'].keys()))
    except Exception as e:
        print(f"Error getting column info: {e}")
        return
    
    # Configure metrics
    print("\nConfiguring data quality metrics...")
    
    # 1. Completeness metric (checks for missing values)
    completeness = CompletenessMetric()
    grader.add_metric("completeness", completeness)
    print("✓ Added completeness metric")
    
    # 2. Accuracy metric with custom validation rules
    accuracy = AccuracyMetric()
    
    # Ask user if they want to configure validation rules
    configure_rules = input("\nDo you want to configure validation rules? (y/n): ").lower().startswith('y')
    
    if configure_rules:
        # Let user select columns for numeric range checks
        numeric_columns = []
        for col_name, col_info in column_info['columns'].items():
            if 'int' in col_info.get('dtype', '').lower() or 'float' in col_info.get('dtype', '').lower():
                numeric_columns.append(col_name)
        
        if numeric_columns:
            print("\nAvailable numeric columns:")
            for i, col in enumerate(numeric_columns, 1):
                print(f"{i}. {col}")
            
            selected = input("Enter column numbers to add range checks (comma-separated, or 'all'): ")
            
            if selected.lower() == 'all':
                selected_cols = numeric_columns
            else:
                try:
                    selected_indices = [int(idx.strip()) - 1 for idx in selected.split(',') if idx.strip()]
                    selected_cols = [numeric_columns[idx] for idx in selected_indices if 0 <= idx < len(numeric_columns)]
                except (ValueError, IndexError):
                    print("Invalid selection, no range checks added")
                    selected_cols = []
            
            # Add range checks for selected columns
            for col in selected_cols:
                min_val = input(f"Enter minimum value for {col} (or press Enter for no minimum): ")
                max_val = input(f"Enter maximum value for {col} (or press Enter for no maximum): ")
                
                min_val = float(min_val) if min_val.strip() else None
                max_val = float(max_val) if max_val.strip() else None
                
                if min_val is not None or max_val is not None:
                    accuracy.add_range_check(col, min_value=min_val, max_value=max_val)
                    print(f"✓ Added range check for {col}: min={min_val}, max={max_val}")
    else:
        # Add some reasonable default checks based on column data types
        numeric_cols_added = 0
        for col_name, col_info in column_info['columns'].items():
            dtype = col_info.get('dtype', '').lower()
            if 'int' in dtype or 'float' in dtype:
                if 'price' in col_name.lower() or 'amount' in col_name.lower() or 'cost' in col_name.lower():
                    accuracy.add_range_check(col_name, min_value=0)
                    numeric_cols_added += 1
                elif 'quantity' in col_name.lower() or 'count' in col_name.lower():
                    accuracy.add_range_check(col_name, min_value=0)
                    numeric_cols_added += 1
        
        if numeric_cols_added > 0:
            print(f"✓ Added automatic range checks for {numeric_cols_added} numeric columns")
    
    grader.add_metric("accuracy", accuracy)
    print("✓ Added accuracy metric")
    
    # Grade the data
    print("\nGrading data quality...")
    try:
        results = grader.grade()
        
        # Display summary results
        print("\nResults Summary:")
        for metric_name, metric_data in results.get('metrics', {}).items():
            score = metric_data.get('score', 0) * 100
            status = metric_data.get('status', 'unknown')
            print(f"  {metric_name.title()}: {score:.1f}% ({status})")
            
            # Show details for failing columns
            if metric_name == 'completeness' and 'columns' in metric_data:
                incomplete_cols = []
                for col, col_data in metric_data['columns'].items():
                    if col_data.get('status', '') == 'failed':
                        incomplete_cols.append(f"{col} ({col_data.get('completeness', 0)*100:.1f}%)")
                
                if incomplete_cols:
                    print(f"    Columns with missing values: {', '.join(incomplete_cols)}")
            
            elif metric_name == 'accuracy' and 'details' in metric_data:
                inaccurate_cols = []
                for col, col_data in metric_data.get('details', {}).items():
                    if 'invalid' in col_data and col_data['invalid'] > 0:
                        inaccurate_cols.append(f"{col} ({col_data['invalid']} invalid values)")
                
                if inaccurate_cols:
                    print(f"    Columns with invalid values: {', '.join(inaccurate_cols)}")
        
        # Generate recommendations
        recommendations = []
        metrics_data = results.get('metrics', {})
        
        # Completeness recommendations
        if 'completeness' in metrics_data:
            completeness_score = metrics_data['completeness'].get('score', 1.0)
            if completeness_score < 0.95:
                # Find columns with most missing values
                columns_data = metrics_data['completeness'].get('columns', {})
                problem_columns = []
                
                for col, col_data in columns_data.items():
                    if col_data.get('completeness', 1.0) < 0.9:
                        problem_columns.append(col)
                
                if problem_columns:
                    recommendations.append({
                        "title": f"Address Missing Values",
                        "priority": "high" if completeness_score < 0.8 else "medium",
                        "description": f"Missing values detected in columns: {', '.join(problem_columns)}",
                        "steps": [
                            "Identify the causes of missing data",
                            "Implement data validation in forms/entry points",
                            "Consider appropriate default values or imputation methods"
                        ]
                    })
        
        # Accuracy recommendations
        if 'accuracy' in metrics_data:
            accuracy_score = metrics_data['accuracy'].get('score', 1.0)
            if accuracy_score < 0.95:
                # Find columns with validation failures
                details = metrics_data['accuracy'].get('details', {})
                problem_columns = []
                
                for col, col_data in details.items():
                    if col_data.get('invalid', 0) > 0:
                        problem_columns.append(col)
                
                if problem_columns:
                    recommendations.append({
                        "title": "Fix Data Validation Issues",
                        "priority": "high" if accuracy_score < 0.8 else "medium",
                        "description": f"Invalid values detected in columns: {', '.join(problem_columns)}",
                        "steps": [
                            "Review data validation rules",
                            "Implement stricter data entry validation",
                            "Clean existing data to meet validation requirements"
                        ]
                    })
        
        # Add recommendations to results
        results['recommendations'] = recommendations
        
        # Add a title and description
        results['title'] = f"Excel Quality Assessment: {os.path.basename(file_path)}"
        results['description'] = f"Analysis of data quality in sheet '{active_sheet}'"
        
        # Generate HTML report
        print("\nGenerating HTML report...")
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"excel_report_{os.path.splitext(os.path.basename(file_path))[0]}_{timestamp}.html"
        report_path = os.path.join(output_dir, report_filename)
        
        generate_html_report(results, report_path)
        
        print(f"\nReport generated successfully: {report_path}")
        
        # Ask if user wants to open the report
        open_report = input("\nOpen the report in your browser? (y/n): ").lower().startswith('y')
        if open_report:
            import webbrowser
            webbrowser.open('file://' + os.path.abspath(report_path))
    
    except Exception as e:
        print(f"Error during grading: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
