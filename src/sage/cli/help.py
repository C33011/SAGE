"""
Help functionality for SAGE.

This module provides interactive documentation and examples.
"""

import sys
import textwrap
import importlib
import inspect
from typing import Dict, List, Optional, Any

def show_help(topic: Optional[str] = None) -> None:
    """
    Display help information about SAGE.
    
    Args:
        topic: Optional specific topic to show help for
    """
    if topic is None:
        _show_general_help()
    else:
        _show_topic_help(topic)

def _show_general_help() -> None:
    """Display general help information."""
    print(textwrap.dedent("""
    SAGE - Spreadsheet Analysis Grading Engine
    ==========================================
    
    SAGE helps you assess and grade data quality in spreadsheets and databases.
    
    Main components:
    
    - Graders: Classes for grading different data sources
      (sage.graders.excel_grader, sage.graders.database_grader)
    
    - Metrics: Quality metrics to assess data
      (sage.metrics.completeness, sage.metrics.accuracy, etc.)
    
    - Reports: Generate reports from quality assessments
      (sage.reports.generator)
    
    - Data: Load and profile data
      (sage.data.loader, sage.data.profiler)
    
    Examples:
    
    - To get help on a specific module: sage.help("graders")
    - To get help on a specific class: sage.help("ExcelGrader")
    
    For more information, visit the full documentation at:
    https://github.com/YourUsername/SAGE/docs
    """))

def _show_topic_help(topic: str) -> None:
    """
    Display help for a specific topic.
    
    Args:
        topic: Topic to show help for (module, class, or function name)
    """
    # Remove 'sage.' prefix if present
    if topic.startswith('sage.'):
        topic = topic[5:]
    
    # Try to find the object in the sage package
    try:
        # First try direct import
        module_parts = topic.split('.')
        if len(module_parts) > 1:
            # It's a module path
            module_name = f"sage.{topic}"
            obj = importlib.import_module(module_name)
        else:
            # It might be a class or function name - search for it
            obj = _find_object_by_name(topic)
            
        if obj:
            # Display the object's docstring
            print("\n", "-" * 80)
            print(f"Help for: {topic}")
            print("-" * 80)
            
            if obj.__doc__:
                print(textwrap.dedent(obj.__doc__))
            else:
                print("No documentation available.")
                
            # If it's a module, list its contents
            if inspect.ismodule(obj):
                print("\nContents:")
                for name, item in inspect.getmembers(obj):
                    if not name.startswith('_'):  # Skip private/internal objects
                        kind = type(item).__name__
                        if inspect.isclass(item) or inspect.isfunction(item):
                            print(f"- {name}: {kind}")
            
            print("-" * 80)
        else:
            print(f"Topic '{topic}' not found in SAGE.")
            
    except (ImportError, AttributeError) as e:
        print(f"Error finding help for '{topic}': {e}")
        print("Try a more general topic or check the spelling.")

def _find_object_by_name(name: str) -> Any:
    """
    Search for an object by name within the sage package.
    
    Args:
        name: Name to search for
        
    Returns:
        The found object or None
    """
    # List of common modules to search in
    modules_to_search = [
        'sage.graders.excel_grader',
        'sage.graders.database_grader',
        'sage.metrics.completeness',
        'sage.metrics.accuracy',
        'sage.metrics.consistency',
        'sage.metrics.timeliness',
        'sage.data.loader',
        'sage.data.profiler',
        'sage.reports.generator'
    ]
    
    # Search each module for the object
    for module_name in modules_to_search:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, name):
                return getattr(module, name)
        except ImportError:
            continue
    
    return None
