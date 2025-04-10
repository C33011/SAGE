SAGE Documentation
=================

**S**\ preadsheet **A**\ nalysis **G**\ rading **E**\ ngine

Welcome to SAGE, a comprehensive toolkit for assessing and grading data quality in spreadsheets and databases.

.. image:: _static/sage_banner.png
   :alt: SAGE Banner
   :align: center

Key Features
-----------

* **Powerful Metrics**: Assess data completeness, accuracy, consistency, timeliness, and more
* **Flexible Framework**: Works with Excel files, CSV, and various database systems
* **Interactive Reports**: Generate detailed HTML reports with visualizations
* **Extensible Design**: Add custom metrics and data sources with ease
* **Production Ready**: Comprehensive error handling and logging

Quick Start
----------

Install SAGE:

.. code-block:: bash

   pip install sage-data-quality

Analyze an Excel file:

.. code-block:: python

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

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user_guide/index
   modules/index
   examples
   changelog
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
