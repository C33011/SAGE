"""
Core analyzer for SAGE.

This module provides the central analysis engine that orchestrates the
execution of data quality metrics and consolidates their results.
"""

import logging
import pandas as pd
import datetime
from typing import Dict, List, Any, Optional, Union

from sage.metrics import (
    AccuracyMetric,
    CompletenessMetric,
    ConsistencyMetric,
    TimelinessMetric
)

# Set up logger
logger = logging.getLogger("sage.core.analyzer")

class Analyzer:
    """
    Main analyzer for data quality assessment.
    
    This class orchestrates the execution of various data quality metrics
    and combines their results into a comprehensive assessment.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the analyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.metrics = {}
        self.results = {}
        logger.debug("Initialized analyzer")
        
        # Set up default metrics
        self._setup_default_metrics()
    
    def _setup_default_metrics(self) -> None:
        """Set up default metrics with standard configurations."""
        # Completeness metric
        completeness = CompletenessMetric("completeness")
        self.add_metric(completeness)
        
        # Accuracy metric
        accuracy = AccuracyMetric("accuracy")
        self.add_metric(accuracy)
        
        # Consistency metric
        consistency = ConsistencyMetric("consistency")
        self.add_metric(consistency)
        
        # Timeliness metric (if date fields exist)
        timeliness = TimelinessMetric("timeliness")
        self.add_metric(timeliness)
        
        logger.debug("Set up default metrics")
    
    def add_metric(self, metric: Any, name: Optional[str] = None) -> None:
        """
        Add a metric to the analyzer.
        
        Args:
            metric: Metric instance to add
            name: Optional name to use (defaults to metric.name)
        """
        metric_name = name or getattr(metric, 'name', f"metric_{len(self.metrics)}")
        self.metrics[metric_name] = metric
        logger.debug(f"Added metric: {metric_name}")
    
    def analyze(self, 
               df: pd.DataFrame, 
               metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze a dataframe using configured metrics.
        
        Args:
            df: Pandas DataFrame to analyze
            metrics: Optional list of metric names to run (runs all if None)
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting analysis on DataFrame with {len(df)} rows, {len(df.columns)} columns")
        start_time = datetime.datetime.now()
        
        # Determine which metrics to run
        metrics_to_run = {}
        if metrics:
            # Filter to only the requested metrics
            for name in metrics:
                if name in self.metrics:
                    metrics_to_run[name] = self.metrics[name]
                else:
                    logger.warning(f"Requested metric '{name}' not found")
        else:
            # Use all configured metrics
            metrics_to_run = self.metrics
        
        if not metrics_to_run:
            logger.warning("No metrics to run")
            return {"error": "No metrics configured"}
        
        # Run each metric and collect results
        results = {}
        for name, metric in metrics_to_run.items():
            try:
                logger.info(f"Running metric: {name}")
                metric_start = datetime.datetime.now()
                
                # Apply the metric to the dataframe
                metric_result = metric.evaluate(df)
                
                # Store the result
                results[name] = metric_result
                
                metric_duration = (datetime.datetime.now() - metric_start).total_seconds()
                logger.info(f"Metric '{name}' completed in {metric_duration:.2f} seconds with "
                           f"score: {metric_result.get('score', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Error running metric '{name}': {str(e)}", exc_info=True)
                # Store the error but don't fail the whole analysis
                results[name] = {
                    "error": str(e),
                    "status": "failed",
                    "score": 0
                }
        
        # Calculate overall score and status
        overall_score, overall_status = self._calculate_overall_score(results)
        
        # Calculate timing
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Create final results dictionary
        final_results = {
            "overall_score": overall_score,
            "overall_status": overall_status,
            "metrics": results,
            "analysis_time": duration,
            "analysis_date": start_time.isoformat()
        }
        
        # Generate recommendations based on results
        recommendations = self._generate_recommendations(results, df)
        if recommendations:
            final_results["recommendations"] = recommendations
        
        # Store the results
        self.results = final_results
        
        logger.info(f"Analysis completed in {duration:.2f} seconds with overall score: {overall_score:.2%}")
        
        return final_results
    
    def _calculate_overall_score(self, 
                               results: Dict[str, Dict[str, Any]]) -> tuple:
        """
        Calculate the overall score and status from metric results.
        
        Args:
            results: Dictionary of metric results
            
        Returns:
            Tuple of (overall_score, overall_status)
        """
        # Extract scores from each metric result
        scores = []
        for metric_name, metric_result in results.items():
            if isinstance(metric_result, dict) and 'score' in metric_result:
                score = metric_result['score']
                if isinstance(score, (int, float)) and 0 <= score <= 1:
                    scores.append(score)
        
        # Calculate the average score if there are any valid scores
        if scores:
            overall_score = sum(scores) / len(scores)
        else:
            overall_score = 0
        
        # Determine overall status based on score
        if overall_score >= 0.95:
            overall_status = "passed"
        elif overall_score >= 0.8:
            overall_status = "warning"
        else:
            overall_status = "failed"
        
        return overall_score, overall_status
    
    def _generate_recommendations(self, 
                                results: Dict[str, Dict[str, Any]],
                                df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on analysis results.
        
        Args:
            results: Dictionary of metric results
            df: The analyzed DataFrame
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Analyze completeness issues
        if 'completeness' in results:
            completeness = results['completeness']
            if completeness.get('status') in ('failed', 'warning'):
                # Find columns with low completeness
                if 'columns' in completeness:
                    low_completeness_cols = []
                    for col, col_data in completeness['columns'].items():
                        if col_data.get('status') == 'failed':
                            low_completeness_cols.append((col, col_data.get('completeness', 0)))
                    
                    # Sort by completeness (lowest first)
                    low_completeness_cols.sort(key=lambda x: x[1])
                    
                    if low_completeness_cols:
                        # Create recommendation for most problematic columns
                        worst_cols = [col for col, _ in low_completeness_cols[:3]]
                        recommendations.append({
                            "title": "Improve Data Completeness",
                            "priority": "high" if completeness.get('status') == 'failed' else "medium",
                            "description": f"Address missing values in columns: {', '.join(worst_cols)}",
                            "affected_metrics": ["completeness"],
                            "affected_columns": worst_cols,
                            "steps": [
                                "Identify the root cause of missing data",
                                "Implement validation in data entry systems",
                                "Consider backfilling missing historical data where possible"
                            ]
                        })
        
        # Analyze consistency issues
        if 'consistency' in results:
            consistency = results['consistency']
            if consistency.get('status') in ('failed', 'warning'):
                # Check for relationship issues
                relationship_issues = False
                if 'details' in consistency and 'relationships' in consistency['details']:
                    for rel_key, rel_data in consistency['details']['relationships'].items():
                        if rel_data.get('status') in ('failed', 'warning'):
                            relationship_issues = True
                            break
                
                if relationship_issues:
                    recommendations.append({
                        "title": "Enforce Data Relationships",
                        "priority": "medium",
                        "description": "Some relationships between columns are inconsistent. Ensure proper constraints are enforced.",
                        "affected_metrics": ["consistency"],
                        "steps": [
                            "Review relationship violations",
                            "Add validation rules to prevent inconsistencies",
                            "Fix existing inconsistent data"
                        ]
                    })
        
        # Analyze accuracy issues
        if 'accuracy' in results:
            accuracy = results['accuracy']
            if accuracy.get('status') in ('failed', 'warning'):
                # Find columns with accuracy issues
                if 'details' in accuracy:
                    problem_cols = []
                    for col, col_data in accuracy['details'].items():
                        if col_data.get('status') == 'failed':
                            problem_cols.append(col)
                    
                    if problem_cols:
                        recommendations.append({
                            "title": "Fix Data Accuracy Issues",
                            "priority": "high" if accuracy.get('status') == 'failed' else "medium",
                            "description": f"Address accuracy problems in columns: {', '.join(problem_cols[:3])}",
                            "affected_metrics": ["accuracy"],
                            "affected_columns": problem_cols[:3],
                            "steps": [
                                "Review invalid data values",
                                "Implement stronger validation rules",
                                "Consider standardizing data formats"
                            ]
                        })
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_pct = duplicate_count / len(df)
            priority = "high" if duplicate_pct > 0.05 else "medium" if duplicate_pct > 0.01 else "low"
            
            recommendations.append({
                "title": "Remove Duplicate Records",
                "priority": priority,
                "description": f"Found {duplicate_count} duplicate rows ({duplicate_pct:.1%} of data)",
                "affected_metrics": ["consistency"],
                "steps": [
                    "Implement unique constraints",
                    "Review and remove duplicates",
                    "Add validation to prevent duplicate creation"
                ]
            })
        
        # Add general recommendation if no specific ones were created
        if not recommendations:
            recommendations.append({
                "title": "Review Data Quality Issues",
                "priority": "medium",
                "description": "Review the detailed metrics results to identify specific areas for improvement.",
                "steps": [
                    "Focus on metrics with lower scores",
                    "Create a data quality improvement plan",
                    "Implement automated validation and monitoring"
                ]
            })
        
        return recommendations
