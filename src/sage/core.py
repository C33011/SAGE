"""
Core engine for SAGE.

This module provides the central coordination point for all SAGE operations,
managing graders, metrics, and report generation.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Type

# Set up logging
logger = logging.getLogger("sage")


class SageEngine:
    """
    Main SAGE engine that coordinates all data quality assessment operations.
    
    This class serves as the primary interface for users of the SAGE library,
    providing methods to configure graders, apply metrics, and generate reports.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the SAGE engine.
        
        Args:
            config_path: Optional path to a JSON configuration file
        """
        self.graders = {}  # Will store active grader instances
        self.config = {}   # Will store configuration
        
        # Load config if provided
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
            
        logger.info("SAGE Engine initialized")
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    def add_grader(self, name: str, grader_instance: Any) -> None:
        """
        Add a grader to the SAGE engine.
        
        Args:
            name: Name to identify this grader
            grader_instance: An instance of a grader class
        """
        self.graders[name] = grader_instance
        logger.debug(f"Added grader: {name}")
    
    def get_grader(self, name: str) -> Any:
        """
        Retrieve a grader by name.
        
        Args:
            name: Name of the grader to retrieve
            
        Returns:
            The grader instance
            
        Raises:
            KeyError: If no grader with the given name exists
        """
        if name not in self.graders:
            raise KeyError(f"No grader named '{name}' has been registered")
        return self.graders[name]
    
    def run_assessment(self, 
                      grader_name: Optional[str] = None,
                      source: Optional[Any] = None,
                      metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run a data quality assessment using the specified grader and metrics.
        
        Args:
            grader_name: Name of grader to use (if None, uses all graders)
            source: Data source to assess (if None, uses previously connected source)
            metrics: List of metrics to apply (if None, uses all available metrics)
            
        Returns:
            Dictionary containing assessment results
        """
        results = {}
        
        # Determine which graders to use
        graders_to_run = [self.graders[grader_name]] if grader_name else self.graders.values()
        
        for grader in graders_to_run:
            # Connect to source if provided
            if source:
                grader.connect(source)
                
            # Run the grading
            grader_results = grader.grade()
            results[grader.name] = grader_results
            
            logger.info(f"Completed assessment with grader: {grader.name}")
        
        return results
    
    def generate_report(self, 
                       results: Dict[str, Any],
                       report_format: str = "html",
                       output_path: Optional[str] = None) -> str:
        """
        Generate a report from assessment results.
        
        Args:
            results: Assessment results as returned by run_assessment()
            report_format: Format for the report ('html', 'json', etc.)
            output_path: Where to save the report (if None, returns as string)
            
        Returns:
            Path to the report or the report content as a string
        """
        # This is a placeholder - will be connected to report generators
        logger.info(f"Generating {report_format} report")
        
        # In the future, we'll use a report factory to create the right report type
        if report_format.lower() == "html":
            # This will be replaced with proper HTML report generation
            report = "<html><body><h1>SAGE Assessment Report</h1></body></html>"
        else:
            # Default to JSON for now
            report = json.dumps(results, indent=2)
            
        # Write to file if path provided :3
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to {output_path}")
            return output_path
        
        return report
