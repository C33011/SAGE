"""
Template engine for SAGE reports.

This module provides functionality to render templates for report generation,
supporting various template formats and customization options.
"""

import os
import re
import logging
import json
from typing import Dict, List, Any, Optional, Union, Callable
from string import Template
from pathlib import Path
import datetime
import html

# Set up logger
logger = logging.getLogger("sage.utils.template")


class TemplateEngine:
    """
    Template rendering engine for SAGE reports.
    
    This class provides functionality to load and render templates,
    with support for variable substitution, conditional blocks,
    and simple loops.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template engine.
        
        Args:
            templates_dir: Optional directory containing template files
        """
        self.templates_dir = templates_dir
        self.templates = {}  # Cached templates
        self.filters = self._get_default_filters()
        
        logger.debug(f"Initialized template engine with directory: {templates_dir}")
    
    def _get_default_filters(self) -> Dict[str, Callable]:
        """
        Get the default template filters.
        
        Returns:
            Dictionary of filter name to filter function
        """
        return {
            "json": json.dumps,
            "html_escape": html.escape,
            "upper": lambda x: str(x).upper(),
            "lower": lambda x: str(x).lower(),
            "title": lambda x: str(x).title(),
            "date": lambda x, fmt="%Y-%m-%d": 
                x.strftime(fmt) if isinstance(x, datetime.datetime) else str(x),
            "number": lambda x, decimals=2: f"{float(x):.{decimals}f}",
            "round": lambda x, decimals=0: round(float(x), decimals),
            "percent": lambda x, decimals=1: f"{float(x) * 100:.{decimals}f}%",
            "truncate": lambda x, length=50: 
                str(x)[:length] + "..." if len(str(x)) > length else str(x),
            "default": lambda x, default_value="": x if x is not None else default_value,
            "length": lambda x: len(x) if hasattr(x, "__len__") else 0,
            "join": lambda x, sep=", ": sep.join(str(i) for i in x) if isinstance(x, (list, tuple)) else str(x),
        }
    
    def add_filter(self, name: str, filter_func: Callable) -> None:
        """
        Add a custom template filter.
        
        Args:
            name: Name of the filter
            filter_func: Filter function
        """
        self.filters[name] = filter_func
        logger.debug(f"Added template filter: {name}")
    
    def load_template(self, name: str) -> str:
        """
        Load a template from the templates directory.
        
        Args:
            name: Template name or path
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Return cached template if available
        if name in self.templates:
            return self.templates[name]
        
        # Determine template path
        if self.templates_dir:
            # First try with the templates directory
            template_path = os.path.join(self.templates_dir, name)
            if not os.path.exists(template_path):
                # Try adding .html extension
                template_path = os.path.join(self.templates_dir, f"{name}.html")
        else:
            # Use name directly as path
            template_path = name
        
        # Check if template exists
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        # Load template content
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Cache the template
        self.templates[name] = template_content
        
        logger.debug(f"Loaded template: {name}")
        return template_content
    
    def set_template_string(self, name: str, content: str) -> None:
        """
        Set a template from a string.
        
        Args:
            name: Template name
            content: Template content
        """
        self.templates[name] = content
        logger.debug(f"Set template string: {name}")
    
    def _process_conditionals(self, template: str, data: Dict[str, Any]) -> str:
        """
        Process conditional blocks in the template.
        
        Args:
            template: Template string
            data: Template data
            
        Returns:
            Processed template string
        """
        # Process if blocks - format: {% if condition %}...{% endif %}
        pattern = r"{%\s*if\s+([^%]+)\s*%}(.*?)(?:{%\s*else\s*%}(.*?))?{%\s*endif\s*%}"
        
        def evaluate_condition(match):
            condition = match.group(1).strip()
            if_content = match.group(2)
            else_content = match.group(3) if match.lastindex >= 3 else ""
            
            # Simple evaluation - just check if the variable exists and is truthy
            parts = condition.split('.')
            value = data
            
            try:
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    elif hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        value = None
                        break
                
                if value:
                    return if_content
                else:
                    return else_content
            except Exception:
                return else_content
        
        # Process all conditionals
        result = re.sub(pattern, evaluate_condition, template, flags=re.DOTALL)
        return result
    
    def _process_loops(self, template: str, data: Dict[str, Any]) -> str:
        """
        Process loop blocks in the template.
        
        Args:
            template: Template string
            data: Template data
            
        Returns:
            Processed template string
        """
        # Process for loops - format: {% for item in items %}...{% endfor %}
        pattern = r"{%\s*for\s+(\w+)\s+in\s+([^%]+)\s*%}(.*?){%\s*endfor\s*%}"
        
        def process_loop(match):
            item_name = match.group(1)
            collection_name = match.group(2).strip()
            loop_content = match.group(3)
            
            # Get the collection from data
            parts = collection_name.split('.')
            collection = data
            
            try:
                for part in parts:
                    if isinstance(collection, dict):
                        collection = collection.get(part)
                    elif hasattr(collection, part):
                        collection = getattr(collection, part)
                    else:
                        collection = None
                        break
                
                if not collection or not hasattr(collection, "__iter__"):
                    return ""  # No collection or not iterable
                
                # Render the loop content for each item
                result = []
                for i, item in enumerate(collection):
                    # Create a context with the item and loop variables
                    loop_data = data.copy()
                    loop_data[item_name] = item
                    loop_data["loop"] = {
                        "index": i + 1,
                        "index0": i,
                        "first": i == 0,
                        "last": i == len(collection) - 1,
                        "length": len(collection)
                    }
                    
                    # Render the content for this item
                    item_result = self._replace_variables(loop_content, loop_data)
                    result.append(item_result)
                
                return "".join(result)
            except Exception as e:
                logger.error(f"Error processing loop: {str(e)}")
                return ""
        
        # Process all loops
        result = re.sub(pattern, process_loop, template, flags=re.DOTALL)
        return result
    
    def _apply_filter(self, value: Any, filter_name: str, args: List[str]) -> Any:
        """
        Apply a filter to a value.
        
        Args:
            value: Value to filter
            filter_name: Filter name
            args: Filter arguments
            
        Returns:
            Filtered value
        """
        if filter_name not in self.filters:
            logger.warning(f"Unknown filter: {filter_name}")
            return value
        
        filter_func = self.filters[filter_name]
        
        try:
            # Convert args to proper types if possible
            processed_args = []
            for arg in args:
                # Remove quotes for string args
                if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                    processed_args.append(arg[1:-1])
                
                # Convert numeric args
                elif arg.isdigit():
                    processed_args.append(int(arg))
                elif arg.replace('.', '', 1).isdigit():
                    processed_args.append(float(arg))
                else:
                    processed_args.append(arg)
            
            # Apply the filter
            if processed_args:
                return filter_func(value, *processed_args)
            else:
                return filter_func(value)
        except Exception as e:
            logger.error(f"Error applying filter {filter_name}: {str(e)}")
            return value
    
    def _replace_variables(self, template: str, data: Dict[str, Any]) -> str:
        """
        Replace variables in the template.
        
        Args:
            template: Template string
            data: Template data
            
        Returns:
            Template with variables replaced
        """
        # Pattern for variables with optional filters: {{ variable | filter1 | filter2(arg1, arg2) }}
        pattern = r"{{\s*([^|{}]+)(\s*\|\s*[^{}]+)?\s*}}"
        
        def replace_var(match):
            var_path = match.group(1).strip()
            filters_part = match.group(2)
            
            # Get the variable value from the data
            parts = var_path.split('.')
            value = data
            
            try:
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    elif hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        value = None
                        break
                
                # Apply filters if present
                if filters_part:
                    filters = filters_part.split('|')
                    
                    for filter_expr in filters:
                        if not filter_expr.strip():
                            continue
                        
                        # Extract filter name and arguments
                        if '(' in filter_expr:
                            filter_name = filter_expr.split('(')[0].strip()
                            args_str = filter_expr.split('(')[1].split(')')[0]
                            args = [arg.strip() for arg in args_str.split(',')]
                        else:
                            filter_name = filter_expr.strip()
                            args = []
                        
                        # Apply the filter
                        value = self._apply_filter(value, filter_name, args)
                
                # Convert to string for output (except None)
                if value is None:
                    return ""
                return str(value)
            except Exception as e:
                logger.error(f"Error rendering variable {var_path}: {str(e)}")
                return f"{{{{ ERROR: {var_path} }}}}"
        
        # Replace all variables
        result = re.sub(pattern, replace_var, template)
        return result
    
    def render(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render a template with the provided data.
        
        Args:
            template_name: Template name or path
            data: Template data
            
        Returns:
            Rendered template
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Load the template
        template_content = self.load_template(template_name)
        
        # Copy data to avoid modifying the original
        context = data.copy()
        
        # Add some useful variables to the context
        context.setdefault("now", datetime.datetime.now())
        
        # Process the template
        # Order matters: conditionals, loops, then variables
        result = template_content
        result = self._process_conditionals(result, context)
        result = self._process_loops(result, context)
        result = self._replace_variables(result, context)
        
        logger.debug(f"Rendered template: {template_name}")
        return result
    
    def render_string(self, template_str: str, data: Dict[str, Any]) -> str:
        """
        Render a template string with the provided data.
        
        Args:
            template_str: Template string
            data: Template data
            
        Returns:
            Rendered template
        """
        # Generate a unique name for this template string
        template_name = f"string_template_{id(template_str)}"
        
        # Cache the template
        self.set_template_string(template_name, template_str)
        
        # Render the template
        return self.render(template_name, data)
    
    def render_to_file(self, template_name: str, data: Dict[str, Any], 
                       output_path: str) -> str:
        """
        Render a template and save the result to a file.
        
        Args:
            template_name: Template name or path
            data: Template data
            output_path: Path to save the rendered template
            
        Returns:
            Path to the output file
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Render the template
        result = self.render(template_name, data)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Write the result to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        logger.info(f"Rendered template {template_name} to file: {output_path}")
        return output_path
