"""
Example: Generating custom HTML reports with SAGE.

This example demonstrates how to:
1. Create a custom template for HTML reports
2. Load and analyze data with SAGE
3. Generate a customized HTML report with the results
"""

import os
import sys
import pandas as pd
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
from sage.metrics.consistency import ConsistencyMetric
from sage.reports.generator import generate_html_report


def create_example_data():
    """Create an example dataset with some quality issues for demonstration."""
    print("Creating example dataset...")
    
    # Create a directory for example data if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Create a dataframe with various data quality issues
    data = {
        'id': range(1, 21),
        'name': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', None, 
                'Eve Wilson', 'Charlie Davis', 'Dave Miller', 'Frank Moore', 'Grace Taylor',
                'Harry Anderson', 'Ivy Thomas', 'Jack White', 'Kate Martin', 'Leo Harris',
                'Mia Clark', 'Noah Lewis', 'Olivia Walker', 'Peter Hall', 'Quinn Young'],
        'age': [32, 28, None, 45, 19, 33, 27, 29, None, 31, 
                40, 22, 25, 38, 41, 35, 29, None, 44, 30],
        'email': ['john@example.com', 'jane@example.com', 'bob@example.com', 
                 'alice@example.com', None, 'eve@example.com', 'charlie@example',  # Missing domain
                 'dave@example.com', 'frankexample.com',  # Missing @ symbol
                 'grace@example.com', 'harry@example.com', 'ivy@example.com',
                 'jack@example.com', 'kate@example.com', 'leo@example.com',
                 'mia@example.com', 'noah@example.com', 'olivia@example.com',
                 'peter@example.com', 'quinn@example.com'],
        'signup_date': [
            '2022-01-15', '2022-01-20', '2022-02-10', '2022-02-15', '2022-03-05',
            '2022-03-15', '2022-04-10', '2022-04-20', '2022/05/10',  # Inconsistent format
            '2022/05/25', '2022-06-15', '2022-06-25', '2022-07-10', '2022-07-25',
            '2022-08-10', '2022-08-30', '2022-09-15', '2022-09-30', '2022-10-15',
            '10/30/2022'  # Different format
        ],
        'account_balance': [1500.50, 2700.75, 950.25, 3600.00, 125.50, 
                          5000.00, 750.25, 1250.75, -50.25, 2800.00,
                          1850.50, 920.25, 3300.75, 1600.50, 2200.00,
                          800.25, 4500.50, 950.00, 1700.25, 2300.75],
        'status': ['active', 'active', 'inactive', 'active', 'pending',
                  'active', 'active', 'inactive', 'active', 'active',
                  'pending', 'active', 'inactive', 'active', 'active',
                  'active', 'pending', 'inactive', 'active', 'active']
    }
    
    df = pd.DataFrame(data)
    
    # Save to Excel file
    excel_path = os.path.join(data_dir, 'customer_data.xlsx')
    df.to_excel(excel_path, index=False)
    
    print(f"Example data saved to: {excel_path}")
    return excel_path


def create_custom_template():
    """Create a custom HTML template for reports."""
    print("Creating custom HTML template...")
    
    # Create a directory for templates if it doesn't exist
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # Define a custom template with a different style (This sample file was generated using copilot, as I don't have a good eye for style)
    template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title|default('Custom Data Quality Report') }}</title>
    <style>
        :root {
            /* Custom color palette - using purple theme */
            --primary: #6200ea;
            --primary-light: #9d46ff;
            --primary-dark: #0a00b6;
            --secondary: #ff6d00;
            --background: #f5f5f5;
            --surface: #ffffff;
            --error: #b00020;
            --success: #00c853;
            --warning: #ffd600;
            
            /* Typography */
            --font-main: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            --font-mono: Consolas, monospace;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: var(--font-main);
            background-color: var(--background);
            color: #333;
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
            padding: 30px 20px;
            border-radius: 8px 8px 0 0;
            margin-bottom: 30px;
        }
        
        h1, h2, h3 {
            margin-bottom: 20px;
            color: var(--primary-dark);
        }
        
        header h1 {
            color: white;
        }
        
        .report-meta {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .score-card {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 30px;
            border-left: 5px solid var(--primary);
        }
        
        .score-summary {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
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
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 20px;
            border-top: 5px solid var(--primary-light);
        }
        
        .metric-card h3 {
            color: var(--primary);
            font-size: 1.2em;
            display: flex;
            align-items: center;
        }
        
        .metric-card h3 .status-icon {
            margin-right: 8px;
            font-size: 1.2em;
        }
        
        .metric-score {
            font-size: 2em;
            font-weight: bold;
            margin: 15px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background-color: var(--surface);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        
        th, td {
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background-color: var(--primary-light);
            color: white;
        }
        
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        tr:hover {
            background-color: #f1f1f1;
        }
        
        .recommendations {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .recommendation {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        
        .recommendation:last-child {
            border-bottom: none;
        }
        
        .priority-high {
            color: var(--error);
            font-weight: bold;
        }
        
        .priority-medium {
            color: var(--warning);
            font-weight: bold;
        }
        
        .priority-low {
            color: var(--success);
            font-weight: bold;
        }
        
        footer {
            text-align: center;
            margin-top: 50px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title|default('Data Quality Report') }}</h1>
            <div class="report-meta">
                <p>Generated: {{ now|date("%Y-%m-%d %H:%M") }}</p>
                <p>Analyzed by SAGE (Spreadsheet Analysis Grading Engine)</p>
            </div>
        </header>
        
        <!-- Overall Score Section -->
        <div class="score-card">
            <div class="score-summary">
                <div>
                    <h2>Overall Data Quality</h2>
                    <p>{{ description|default('Summary of data quality assessment') }}</p>
                </div>
                <div class="score-circle {% if overall_score > 0.8 %}score-high{% elif overall_score > 0.6 %}score-medium{% else %}score-low{% endif %}">
                    {{ overall_score|percent }}
                </div>
            </div>
            <p>Status: <strong>{{ overall_status|title }}</strong></p>
        </div>
        
        <!-- Metrics Section -->
        <h2>Quality Metrics</h2>
        <div class="metric-grid">
            {% for name, metric in metrics.items() %}
            <div class="metric-card">
                <h3>
                    <span class="status-icon">
                        {% if metric.status == "passed" %}✓
                        {% elif metric.status == "warning" %}⚠
                        {% elif metric.status == "failed" %}✗
                        {% else %}?{% endif %}
                    </span>
                    {{ name|title }}
                </h3>
                <div class="metric-score">{{ metric.score|percent }}</div>
                <p>{{ metric.message|default('') }}</p>
            </div>
            {% endfor %}
        </div>
        
        <!-- Details Section (if any) -->
        {% if details %}
        <h2>Detailed Analysis</h2>
        {% for section, section_data in details.items() %}
        <div class="section">
            <h3>{{ section|title }}</h3>
            {% if section_data is mapping %}
                <table>
                    <thead>
                        <tr>
                        {% for key in section_data.keys()|list %}
                            <th>{{ key|title }}</th>
                        {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in section_data.values() %}
                        <tr>
                            {% if item is mapping %}
                                {% for value in item.values() %}
                                    <td>{{ value }}</td>
                                {% endfor %}
                            {% else %}
                                <td>{{ item }}</td>
                            {% endif %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>{{ section_data }}</p>
            {% endif %}
        </div>
        {% endfor %}
        {% endif %}
        
        <!-- Recommendations Section -->
        {% if recommendations %}
        <h2>Recommendations</h2>
        <div class="recommendations">
            {% for rec in recommendations %}
            <div class="recommendation">
                <h3>{{ rec.title }}</h3>
                <p class="priority-{{ rec.priority }}">Priority: {{ rec.priority|title }}</p>
                <p>{{ rec.description }}</p>
                {% if rec.steps %}
                <ul>
                    {% for step in rec.steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <footer>
            <p>Generated by SAGE - Spreadsheet Analysis Grading Engine</p>
            <p>Version {{ version|default('0.1.0') }}</p>
        </footer>
    </div>
</body>
</html>
"""
    
    template_path = os.path.join(template_dir, 'custom_report_template.html')
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"Custom template saved to: {template_path}")
    return template_path


def main():
    """Run the example workflow to generate a custom HTML report."""
    print("=" * 80)
    print("SAGE Example: Custom HTML Report Generation")
    print("=" * 80)
    
    # Step 1: Create example data if needed
    excel_path = create_example_data()
    
    # Step 2: Create a custom template
    template_path = create_custom_template()
    
    # Step 3: Set up the grader with metrics
    print("\nSetting up Excel grader with metrics...")
    grader = ExcelGrader(name="Customer Data Analysis")
    
    # Add metrics to the grader
    completeness = CompletenessMetric()
    grader.add_metric("completeness", completeness)
    
    accuracy = AccuracyMetric()
    # Add data validation rules
    accuracy.add_pattern_check("email", r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    accuracy.add_range_check("age", min_value=18, max_value=100)
    accuracy.add_range_check("account_balance", min_value=0)
    grader.add_metric("accuracy", accuracy)
    
    # If ConsistencyMetric doesn't have the expected methods, we need to adapt our approach
    try:
        consistency = ConsistencyMetric()
        # Try to add rules - these might need to be adapted based on the actual API
        # Use hasattr to check if the methods exist before calling them
        if hasattr(consistency, "add_date_format_check"):
            consistency.add_date_format_check("signup_date", "%Y-%m-%d")
        else:
            # Alternative approach if the method doesn't exist
            consistency.add_rule("signup_date", "date_format", format="%Y-%m-%d")
        
        if hasattr(consistency, "add_value_check"):
            consistency.add_value_check("status", ["active", "inactive", "pending"])
        else:
            # Alternative approach
            consistency.add_rule("status", "allowed_values", values=["active", "inactive", "pending"])
        
        grader.add_metric("consistency", consistency)
    except (AttributeError, TypeError) as e:
        print(f"Warning: Could not configure consistency metric: {e}")
        print("Continuing without consistency checks...")
        
        # Create a simple mock consistency metric if needed for the demo
        class MockConsistencyMetric:
            def evaluate(self, df):
                # Calculate a simple consistency score based on date format patterns
                date_col = df['signup_date']
                standard_format = sum(1 for date in date_col if '-' in str(date) and len(str(date).split('-')) == 3)
                consistency_score = standard_format / len(date_col) if len(date_col) > 0 else 1.0
                
                # Create a mock result
                return {
                    "score": consistency_score,
                    "status": "passed" if consistency_score > 0.9 else "warning" if consistency_score > 0.7 else "failed",
                    "message": f"Date format consistency: {consistency_score:.0%} follow standard format",
                    "details": {
                        "date_format": {
                            "consistent": standard_format,
                            "inconsistent": len(date_col) - standard_format
                        }
                    }
                }
        
        # Use the mock metric instead
        grader.add_metric("consistency", MockConsistencyMetric())
    
    # Step 4: Connect to data source
    print("\nConnecting to Excel file...")
    grader.connect(excel_path)
    
    # Print available sheets
    sheets = grader.get_available_sheets()
    print(f"Available sheets: {sheets}")
    
    # Set active sheet (use the first sheet by default)
    grader.set_active_sheet(sheets[0])
    
    # Step 5: Grade the data
    print("\nGrading data...")
    results = grader.grade()
    
    # Step 6: Enrich the results with recommendations
    print("\nAdding recommendations based on results...")
    metrics_data = results.get('metrics', {})
    
    # Gather issues to make recommendations
    recommendations = []
    
    # Check completeness (check comment below the this one)
    if 'completeness' in metrics_data:
        completeness_score = metrics_data['completeness'].get('score', 1.0)
        if completeness_score < 0.9:
            recommendations.append({
                "title": "Address Missing Data",
                "priority": "high" if completeness_score < 0.8 else "medium",
                "description": "There are missing values in the dataset that should be addressed.",
                "steps": [
                    "Identify columns with missing values",
                    "Implement validation to ensure required fields are filled",
                    "Consider appropriate imputation strategies for historical data"
                ]
            })
    
    # Check email accuracy
    if 'accuracy' in metrics_data and 'details' in metrics_data['accuracy']:
        details = metrics_data['accuracy'].get('details', {})
        if 'email' in details:
            email_issues = details.get('email', {})
            if email_issues.get('invalid', 0) > 0:
                recommendations.append({
                    "title": "Fix Invalid Email Addresses",
                    "priority": "high",
                    "description": "Some email addresses do not conform to a valid format.",
                    "steps": [
                        "Identify records with invalid email formats",
                        "Implement email validation in your data entry forms",
                        "Contact customers to update their information"
                    ]
                })
    
    # Check date consistency (check comment below)
    if 'consistency' in metrics_data and metrics_data['consistency'].get('score', 1.0) < 0.9:
        recommendations.append({
            "title": "Standardize Date Formats",
            "priority": "medium",
            "description": "Date formats are inconsistent across the dataset.",
            "steps": [
                "Standardize on YYYY-MM-DD format for all dates",
                "Update data entry forms to enforce consistent formatting",
                "Convert existing dates to the standard format"
            ]
        })
    
    # Add overall data quality recommendation if needed (these were just generated with chatgpt since I didn't feel like making a bunch)
    if results.get('overall_score', 1.0) < 0.8:
        recommendations.append({
            "title": "Implement Data Governance Program",
            "priority": "high",
            "description": "Overall data quality issues suggest a need for stronger data governance.",
            "steps": [
                "Establish data quality standards and metrics",
                "Define data ownership and stewardship roles",
                "Implement regular data quality monitoring",
                "Create a data quality improvement roadmap"
            ]
        })
    
    # Add recommendations to results
    results['recommendations'] = recommendations
    
    # Add a title and description
    results['title'] = "Customer Data Quality Assessment"
    results['description'] = "Analysis of customer data quality including completeness, accuracy, and consistency checks."
    
    # Step 7: Generate the HTML report
    print("\nGenerating custom HTML report...")
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, f"customer_data_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    
    generate_html_report(results, report_path, template_path=template_path)
    
    print("\nDone!")
    print(f"Custom HTML report generated at: {report_path}")
    print("\nOpen this file in your web browser to view the report.")


if __name__ == "__main__":
    main()
