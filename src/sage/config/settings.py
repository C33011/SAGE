"""
Configuration settings for SAGE.

This module provides functionality for loading, validating, and
managing configuration settings for SAGE.
"""

import os
import logging
import json
import yaml
from typing import Dict, Any, Optional

# Set up logger
logger = logging.getLogger("sage.config")

def load_configuration(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to configuration file (JSON or YAML)
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        ValueError: If the file format is not supported or content is invalid
    """
    # Return empty config if no path provided
    if not config_path:
        return {}
    
    # Check if file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Determine file type from extension
    _, ext = os.path.splitext(config_path.lower())
    
    try:
        if ext in ('.json', '.jsonc'):
            # Load JSON configuration
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded JSON configuration from {config_path}")
                
        elif ext in ('.yml', '.yaml'):
            # Load YAML configuration
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded YAML configuration from {config_path}")
                
        else:
            # Default to trying JSON
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path} as JSON")
        
        # Validate configuration
        config = validate_configuration(config)
        
        return config
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {str(e)}")
        raise ValueError(f"Invalid JSON in configuration file: {str(e)}")
        
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in configuration file: {str(e)}")
        raise ValueError(f"Invalid YAML in configuration file: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

def validate_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize configuration values.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Validated configuration dictionary
    """
    # Create a new dictionary to store validated config
    validated = {}
    
    # Validate metrics configuration
    if 'metrics' in config:
        metrics_config = config['metrics']
        validated_metrics = {}
        
        for metric_name, metric_settings in metrics_config.items():
            # Validate each metric configuration
            if not isinstance(metric_settings, dict):
                logger.warning(f"Invalid configuration for metric '{metric_name}': must be a dictionary")
                continue
                
            # Add validated metric config
            validated_metrics[metric_name] = metric_settings
        
        validated['metrics'] = validated_metrics
    
    # Validate data source configuration
    if 'source' in config:
        source_config = config['source']
        
        if not isinstance(source_config, dict):
            logger.warning("Invalid source configuration: must be a dictionary")
        else:
            # Add validated source config
            validated['source'] = source_config
    
    # Validate report configuration
    if 'report' in config:
        report_config = config['report']
        
        if not isinstance(report_config, dict):
            logger.warning("Invalid report configuration: must be a dictionary")
        else:
            # Add validated report config
            validated['report'] = report_config
    
    # Add other top-level keys as-is
    for key, value in config.items():
        if key not in validated:
            validated[key] = value
    
    return validated

def get_default_configuration() -> Dict[str, Any]:
    """
    Get the default configuration settings.
    
    Returns:
        Dictionary of default configuration values
    """
    return {
        "metrics": {
            "completeness": {
                "enabled": True,
                "weight": 1.0,
                "threshold": {
                    "passed": 0.95,
                    "warning": 0.8
                }
            },
            "accuracy": {
                "enabled": True,
                "weight": 1.0,
                "threshold": {
                    "passed": 0.95,
                    "warning": 0.8
                }
            },
            "consistency": {
                "enabled": True,
                "weight": 1.0,
                "threshold": {
                    "passed": 0.95,
                    "warning": 0.8
                }
            },
            "timeliness": {
                "enabled": True,
                "weight": 1.0,
                "threshold": {
                    "passed": 0.95,
                    "warning": 0.8
                }
            }
        },
        "report": {
            "format": "html",
            "include_charts": True,
            "include_recommendations": True
        }
    }

def merge_configurations(default_config: Dict[str, Any], 
                        user_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge user configuration with default configuration.
    
    Args:
        default_config: Default configuration dictionary
        user_config: User-provided configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    merged = default_config.copy()
    
    # Recursively merge dictionaries
    def deep_merge(original, update):
        for key, value in update.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                deep_merge(original[key], value)
            else:
                original[key] = value
    
    deep_merge(merged, user_config)
    return merged
