# SAGE: Spreadsheet Analysis Grading Engine

A comprehensive Python toolkit for assessing and grading data quality in spreadsheets and databases. This has been a personal project of mine to build out a python framework, and I feel confident enough to have community feedback and modification. This project aims to provide a simple-to-use framework that allows for grading and surveying a spreadsheet or database! With 4 metrics to use, you can test for various aspects of a database to find flaws. I encourage modification, so feel free to fork and edit this library! 

## Features

- **Multiple Data Sources**: Works with Excel files, CSVs, and databases
- **Rich Quality Metrics**: Assess completeness, accuracy, consistency, timeliness, and more
- **Interactive Reports**: Generate detailed HTML reports with data quality visualizations
- **Extensible Framework**: Easily add custom metrics and data sources
- **Data Profiling**: Generate comprehensive profiles of your data

## Installation

```bash
pip install sage-data-quality
```

## Quick Start

### Analyzing an Excel file

```python
from sage.graders.excel_grader import ExcelGrader
from sage.metrics.completeness import CompletenessMetric
from sage.metrics.accuracy import AccuracyMetric

# Create a grader
grader = ExcelGrader(name="Customer Data Analysis")

# Add metrics
grader.add_metric("completeness", CompletenessMetric())
grader.add_metric("accuracy", AccuracyMetric())

# Load and grade data
grader.load_excel("customer_data.xlsx")
results = grader.grade()

# Generate a report
from sage.reports.generator import generate_html_report
generate_html_report(results, "data_quality_report.html")
```

### Analyzing a database

```python
from sage.graders.database_grader import DatabaseGrader
from sage.metrics.completeness import CompletenessMetric
from sqlalchemy import create_engine

# Create a grader
grader = DatabaseGrader(name="Customer Database Analysis")

# Add metrics
grader.add_metric("completeness", CompletenessMetric())

# Connect to database
engine = create_engine("sqlite:///customer_data.db")
grader.connect(engine)

# Set table to analyze
grader.set_active_table("customers")

# Grade the data
results = grader.grade()

# Generate a report
from sage.reports.generator import generate_html_report
generate_html_report(results, "database_quality_report.html")
```

## Documentation

Full documentation is available at: https://C33011.github.io/sage/

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib
- sqlalchemy (for database support)
- openpyxl (for Excel support)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
