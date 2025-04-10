"""
CLI output formatters for SAGE.

This module provides functions for formatting and displaying output
in the command-line interface, including tables, colors, and rich text.
"""

import os
import sys
import json
import textwrap
from typing import Dict, List, Any, Optional, Union, Tuple
import datetime


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def supports_color() -> bool:
    """
    Check if the terminal supports color output.
    
    Returns:
        True if color is supported, False otherwise
    """
    # Windows detection
    is_windows = sys.platform.startswith('win')
    
    # Check for NO_COLOR environment variable
    if os.environ.get('NO_COLOR'):
        return False
    
    # Check for FORCE_COLOR environment variable
    if os.environ.get('FORCE_COLOR'):
        return True
    
    # Check if stdout is a TTY
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Windows specific checks
    if is_windows:
        # Check for ANSICON environment variable
        if os.environ.get('ANSICON'):
            return True
        
        # Check for Windows Terminal or ConEmu
        if os.environ.get('WT_SESSION') or os.environ.get('ConEmuANSI') == 'ON':
            return True
        
        # Check for Windows 10 terminal
        import platform
        if platform.release() == '10':
            try:
                from ctypes import windll
                return windll.kernel32.SetConsoleMode(windll.kernel32.GetStdHandle(-11), 7) != 0
            except:
                return False
    
    # For non-Windows, assume color is supported if we get this far
    return True


def colorize(text: str, color: str, use_color: Optional[bool] = None) -> str:
    """
    Add color to text for terminal output.
    
    Args:
        text: Text to colorize
        color: Color code from Colors class
        use_color: Override color support detection
        
    Returns:
        Colorized text if supported, original text otherwise
    """
    if use_color is None:
        use_color = supports_color()
        
    if use_color:
        return f"{color}{text}{Colors.RESET}"
    return text


def format_output(data: Any, format: str = "text") -> str:
    """
    Format output data in various formats.
    
    Args:
        data: Data to format
        format: Output format (text, json, yaml)
        
    Returns:
        Formatted string
    """
    if format == "json":
        return json.dumps(data, indent=2)
    elif format == "yaml":
        import yaml
        return yaml.dump(data, default_flow_style=False)
    else:  # text
        if isinstance(data, dict):
            return "\n".join([f"{k}: {v}" for k, v in data.items()])
        elif isinstance(data, list):
            return "\n".join([str(item) for item in data])
        else:
            return str(data)


def print_banner(text: str, width: int = 80, char: str = "=") -> None:
    """
    Print a banner with the specified text.
    
    Args:
        text: Text to display in the banner
        width: Width of the banner
        char: Character to use for the banner
    """
    use_color = supports_color()
    
    banner_line = char * width
    padding = (width - len(text) - 2) // 2
    text_line = char * padding + " " + text + " " + char * (width - len(text) - padding - 2)
    
    if use_color:
        print(colorize(banner_line, Colors.BRIGHT_CYAN))
        print(colorize(text_line, Colors.BRIGHT_CYAN))
        print(colorize(banner_line, Colors.BRIGHT_CYAN))
    else:
        print(banner_line)
        print(text_line)
        print(banner_line)
    print()


def print_section(title: str, underline: bool = True) -> None:
    """
    Print a section title.
    
    Args:
        title: Section title
        underline: Whether to add an underline
    """
    use_color = supports_color()
    
    if use_color:
        print(colorize(title, Colors.BOLD + Colors.BRIGHT_GREEN))
    else:
        print(title)
        
    if underline:
        if use_color:
            print(colorize("-" * len(title), Colors.BRIGHT_GREEN))
        else:
            print("-" * len(title))
    print()


def print_table(data: List[Dict[str, Any]], 
               columns: Optional[List[str]] = None,
               sort_by: Optional[str] = None,
               max_width: int = 120) -> None:
    """
    Print a table of data.
    
    Args:
        data: List of dictionaries to display as a table
        columns: Optional list of columns to include
        sort_by: Optional column to sort by
        max_width: Maximum width of the table
    """
    if not data:
        print("(No data to display)")
        return
    
    use_color = supports_color()
    
    # Determine columns to display
    if not columns:
        # Get all unique keys from all dictionaries
        columns = list(set().union(*(d.keys() for d in data)))
        
    # Sort data if requested
    if sort_by and sort_by in columns:
        data = sorted(data, key=lambda x: x.get(sort_by, ""))
    
    # Calculate column widths
    col_widths = {}
    for col in columns:
        # Width is the max of the column name and the longest value
        header_width = len(str(col))
        value_width = max((len(str(row.get(col, ""))) for row in data), default=0)
        col_widths[col] = min(max(header_width, value_width), 40)  # Limit column width
    
    # Check if total width exceeds max_width
    total_width = sum(col_widths.values()) + (3 * len(columns)) - 1
    if total_width > max_width:
        # Scale down columns proportionally
        scale_factor = max_width / total_width
        for col in col_widths:
            col_widths[col] = max(10, int(col_widths[col] * scale_factor))
    
    # Print header
    header = " | ".join(str(col).ljust(col_widths[col]) for col in columns)
    if use_color:
        print(colorize(header, Colors.BOLD))
    else:
        print(header)
    
    # Print separator
    separator = "-+-".join("-" * col_widths[col] for col in columns)
    print(separator)
    
    # Print rows
    for row in data:
        row_values = []
        for col in columns:
            value = str(row.get(col, ""))
            # Truncate if too long
            if len(value) > col_widths[col]:
                value = value[:col_widths[col] - 3] + "..."
            row_values.append(value.ljust(col_widths[col]))
        print(" | ".join(row_values))


def print_result(result: Dict[str, Any]) -> None:
    """
    Print the results of an assessment.
    
    Args:
        result: Assessment result dictionary
    """
    # Print banner
    print_banner("SAGE Assessment Results")
    
    # Print metadata
    metadata = result.get("metadata", {})
    print(f"File: {metadata.get('file_path', 'Unknown')}")
    print(f"Rows: {metadata.get('rows', 0):,}")
    print(f"Columns: {metadata.get('columns', 0):,}")
    print(f"Assessment Time: {metadata.get('assessment_time', 0):.2f} seconds")
    print(f"Metrics Used: {', '.join(metadata.get('metrics_used', []))}")
    print()
    
    # Print overall score if available
    if "overall_score" in result:
        score = result["overall_score"]
        status = result.get("overall_status", "unknown")
        
        use_color = supports_color()
        score_str = f"{score:.1%}"
        
        if use_color:
            if status == "passed":
                status_color = Colors.GREEN
            elif status == "warning":
                status_color = Colors.YELLOW
            elif status == "failed":
                status_color = Colors.RED
            else:
                status_color = Colors.RESET
                
            print(f"Overall Score: {colorize(score_str, status_color + Colors.BOLD)}")
            print(f"Status: {colorize(status.title(), status_color + Colors.BOLD)}")
        else:
            print(f"Overall Score: {score_str}")
            print(f"Status: {status.title()}")
        
        print()
    
    # Print metric scores
    metrics = result.get("metrics", {})
    if metrics:
        print_section("Metric Scores")
        
        # Prepare data for table
        metric_data = []
        for metric_name, metric_result in metrics.items():
            score = metric_result.get("score", 0) * 100
            status = metric_result.get("status", "unknown")
            message = metric_result.get("message", "")
            
            # Truncate message if too long
            if len(message) > 50:
                message = message[:47] + "..."
            
            metric_data.append({
                "Metric": metric_name.title(),
                "Score": f"{score:.1f}%",
                "Status": status.title(),
                "Message": message
            })
        
        # Print table
        print_table(metric_data, columns=["Metric", "Score", "Status", "Message"])
        print()
    
    # Print recommendations if available
    recommendations = result.get("recommendations", [])
    if recommendations:
        print_section("Recommendations")
        
        for i, rec in enumerate(recommendations, 1):
            priority = rec.get("priority", "medium")
            title = rec.get("title", f"Recommendation {i}")
            description = rec.get("description", "")
            
            use_color = supports_color()
            if use_color:
                if priority == "high":
                    priority_color = Colors.RED
                elif priority == "medium":
                    priority_color = Colors.YELLOW
                else:
                    priority_color = Colors.GREEN
                    
                print(f"{i}. {colorize(title, Colors.BOLD)}")
                print(f"   Priority: {colorize(priority.title(), priority_color)}")
                print(textwrap.fill(description, width=80, initial_indent="   ", subsequent_indent="   "))
            else:
                print(f"{i}. {title}")
                print(f"   Priority: {priority.title()}")
                print(textwrap.fill(description, width=80, initial_indent="   ", subsequent_indent="   "))
            
            print()


def print_error(message: str) -> None:
    """
    Print an error message.
    
    Args:
        message: Error message to print
    """
    use_color = supports_color()
    
    if use_color:
        print(colorize(f"Error: {message}", Colors.RED), file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """
    Print a warning message.
    
    Args:
        message: Warning message to print
    """
    use_color = supports_color()
    
    if use_color:
        print(colorize(f"Warning: {message}", Colors.YELLOW), file=sys.stderr)
    else:
        print(f"Warning: {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """
    Print a success message.
    
    Args:
        message: Success message to print
    """
    use_color = supports_color()
    
    if use_color:
        print(colorize(f"Success: {message}", Colors.GREEN))
    else:
        print(f"Success: {message}")


def get_terminal_size() -> Tuple[int, int]:
    """
    Get the size of the terminal.
    
    Returns:
        Tuple of (width, height)
    """
    try:
        size = os.get_terminal_size()
        return (size.columns, size.lines)
    except (AttributeError, OSError):
        # Default to 80x24 if terminal size can't be determined
        return (80, 24)
