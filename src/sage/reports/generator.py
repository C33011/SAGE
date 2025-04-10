"""
Report generation functions for SAGE.

This module provides functions to generate data quality reports
in various formats, including HTML, JSON, and CSV.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List, Union
import datetime
import pandas as pd

from sage.reports.html_report import generate_html_report as generate_html

# Set up logger
logger = logging.getLogger("sage.reports.generator")


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
    # Prepare data and enrich with visualization information if needed
    enriched_data = enrich_report_data(data)
    
    # Call the HTML report generator
    return generate_html(enriched_data, output_path, template_path)


def generate_json_report(data: Dict[str, Any], output_path: str) -> bool:
    """
    Generate a JSON report from data quality assessment results.
    
    Args:
        data: Assessment results and metadata
        output_path: Path to write the output JSON file
        
    Returns:
        True if the report was generated successfully
    """
    try:
        logger.info(f"Generating JSON report at: {output_path}")
        
        # Prepare data for JSON serialization
        serializable_data = prepare_for_serialization(data)
        
        # Add timestamp
        serializable_data['generated_at'] = datetime.datetime.now().isoformat()
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2)
            
        logger.info(f"JSON report generated successfully at: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating JSON report: {str(e)}")
        return False


def generate_csv_report(data: Dict[str, Any], output_dir: str) -> bool:
    """
    Generate CSV reports from data quality assessment results.
    Creates multiple CSV files for different aspects of the results.
    
    Args:
        data: Assessment results and metadata
        output_dir: Directory to write CSV files
        
    Returns:
        True if the reports were generated successfully
    """
    try:
        logger.info(f"Generating CSV reports in: {output_dir}")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate summary CSV
        summary_data = []
        metrics = data.get('metrics', {})
        
        for metric_name, metric_data in metrics.items():
            summary_data.append({
                'metric': metric_name,
                'score': metric_data.get('score', None),
                'status': metric_data.get('status', None),
                'message': metric_data.get('message', None)
            })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_path = os.path.join(output_dir, 'summary.csv')
            summary_df.to_csv(summary_path, index=False)
            logger.debug(f"Generated summary CSV: {summary_path}")
        
        # Generate detailed CSVs for each metric
        for metric_name, metric_data in metrics.items():
            if 'columns' in metric_data:
                # Handle column-based metrics (like completeness)
                columns_data = []
                for col_name, col_data in metric_data['columns'].items():
                    col_row = {'column': col_name}
                    col_row.update(col_data)
                    columns_data.append(col_row)
                
                if columns_data:
                    columns_df = pd.DataFrame(columns_data)
                    columns_path = os.path.join(output_dir, f"{metric_name}_columns.csv")
                    columns_df.to_csv(columns_path, index=False)
                    logger.debug(f"Generated {metric_name} columns CSV: {columns_path}")
            
            if 'details' in metric_data:
                # Handle metrics with details (like accuracy)
                details_data = []
                for col_name, col_data in metric_data['details'].items():
                    col_row = {'column': col_name}
                    col_row.update(col_data)
                    details_data.append(col_row)
                
                if details_data:
                    details_df = pd.DataFrame(details_data)
                    details_path = os.path.join(output_dir, f"{metric_name}_details.csv")
                    details_df.to_csv(details_path, index=False)
                    logger.debug(f"Generated {metric_name} details CSV: {details_path}")
        
        # Generate recommendations CSV if available
        recommendations = data.get('recommendations', [])
        if recommendations:
            recs_data = []
            for rec in recommendations:
                rec_row = {
                    'title': rec.get('title', ''),
                    'priority': rec.get('priority', ''),
                    'description': rec.get('description', '')
                }
                recs_data.append(rec_row)
            
            if recs_data:
                recs_df = pd.DataFrame(recs_data)
                recs_path = os.path.join(output_dir, 'recommendations.csv')
                recs_df.to_csv(recs_path, index=False)
                logger.debug(f"Generated recommendations CSV: {recs_path}")
        
        logger.info(f"CSV reports generated successfully in: {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating CSV reports: {str(e)}")
        return False


def enrich_report_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich report data with additional information for visualization.
    
    Args:
        data: Original assessment results
        
    Returns:
        Enriched data with visualization information
    """
    # Make a copy to avoid modifying the original
    enriched = data.copy()
    
    # Add timestamp if not present
    if 'timestamp' not in enriched:
        enriched['timestamp'] = datetime.datetime.now().isoformat()
    
    # Calculate additional metrics if needed
    if 'metrics' in enriched:
        # For completeness metrics, add column-level completeness visualization
        for metric_name, metric_data in enriched.get('metrics', {}).items():
            if metric_name == 'completeness' and 'columns' in metric_data:
                # Will be used by the report template to generate visualizations
                column_scores = {col: data.get('completeness', 0) for col, data in metric_data['columns'].items()}
                enriched['completeness_column_scores'] = column_scores
    
    return enriched


def prepare_for_serialization(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare data for JSON serialization, handling special types.
    
    Args:
        data: Original data
        
    Returns:
        Serializable version of the data
    """
    if isinstance(data, dict):
        return {k: prepare_for_serialization(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [prepare_for_serialization(item) for item in data]
    elif isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    elif isinstance(data, (int, float, str, bool, type(None))):
        return data
    else:
        # Convert other types to strings
        return str(data)
