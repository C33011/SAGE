"""
SAGE CLI commands.

This module provides the command-line interface functionality for SAGE,
including argument parsing and command execution.
"""

import os
import sys
import argparse
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd

from sage.cli.formatters import format_output, print_result, print_table, print_banner
from sage.data.loader import load_data
from sage.core.analyzer import Analyzer
from sage.reports.generator import generate_html_report
from sage.config.settings import load_configuration

# Set up logger
logger = logging.getLogger("sage.cli")


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler()]
    )
    
    # Reduce verbosity of some libraries
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="SAGE - Spreadsheet Analysis Grading Engine",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Assess command
    assess_parser = subparsers.add_parser("assess", help="Assess data quality")
    assess_parser.add_argument(
        "file", 
        help="File to assess (CSV, Excel, etc.)"
    )
    assess_parser.add_argument(
        "--config", "-c",
        help="Configuration file for assessment (JSON or YAML)"
    )
    assess_parser.add_argument(
        "--output", "-o",
        help="Output file for results (JSON)"
    )
    assess_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    assess_parser.add_argument(
        "--metrics",
        nargs="+",
        choices=["accuracy", "completeness", "consistency", "timeliness", "all"],
        default=["all"],
        help="Metrics to include in assessment"
    )
    assess_parser.add_argument(
        "--sheet",
        help="Sheet name for Excel files"
    )
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate a report from assessment results")
    report_parser.add_argument(
        "results",
        help="Assessment results file (JSON)"
    )
    report_parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file for report (HTML)"
    )
    report_parser.add_argument(
        "--format", "-f",
        choices=["html", "pdf", "md"],
        default="html",
        help="Report format"
    )
    report_parser.add_argument(
        "--template", "-t",
        help="Custom template for report"
    )
    report_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Profile command
    profile_parser = subparsers.add_parser("profile", help="Profile a dataset")
    profile_parser.add_argument(
        "file",
        help="File to profile (CSV, Excel, etc.)"
    )
    profile_parser.add_argument(
        "--output", "-o",
        help="Output file for profile results (JSON)"
    )
    profile_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    profile_parser.add_argument(
        "--sample",
        type=int,
        help="Number of rows to sample (0 for all)"
    )
    profile_parser.add_argument(
        "--sheet",
        help="Sheet name for Excel files"
    )
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    return parser.parse_args()


def run_assessment(file_path: str, 
                  config_path: Optional[str] = None,
                  metrics: List[str] = None,
                  sheet_name: Optional[str] = None,
                  output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run a data quality assessment on the specified file.
    
    Args:
        file_path: Path to the data file
        config_path: Optional path to configuration file
        metrics: List of metrics to include
        sheet_name: Sheet name for Excel files
        output_path: Optional path to save results
        
    Returns:
        Assessment results
    """
    logger.info(f"Starting assessment of {file_path}")
    start_time = time.time()
    
    # Load configuration
    config = load_configuration(config_path) if config_path else {}
    
    # Load data
    logger.info("Loading data...")
    df = load_data(file_path, sheet_name=sheet_name)
    logger.info(f"Loaded data with {len(df)} rows and {len(df.columns)} columns")
    
    # Determine which metrics to run
    if not metrics:
        metrics = ["all"]
    
    if "all" in metrics:
        enabled_metrics = ["accuracy", "completeness", "consistency", "timeliness"]
    else:
        enabled_metrics = metrics
    
    logger.info(f"Running assessment with metrics: {', '.join(enabled_metrics)}")
    
    # Create analyzer and run assessment
    analyzer = Analyzer(config=config)
    results = analyzer.analyze(df, metrics=enabled_metrics)
    
    # Add metadata
    elapsed_time = time.time() - start_time
    results["metadata"] = {
        "file_path": file_path,
        "rows": len(df),
        "columns": len(df.columns),
        "assessment_time": round(elapsed_time, 2),
        "metrics_used": enabled_metrics
    }
    
    logger.info(f"Assessment completed in {elapsed_time:.2f} seconds")
    
    # Save results if output path provided
    if output_path:
        import json
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Assessment results saved to {output_path}")
    
    return results


def generate_report(results_path: str,
                   output_path: str,
                   format: str = "html",
                   template_path: Optional[str] = None) -> str:
    """
    Generate a report from assessment results.
    
    Args:
        results_path: Path to assessment results file
        output_path: Path to save the report
        format: Report format (html, pdf, md)
        template_path: Optional custom template path
        
    Returns:
        Path to the generated report
    """
    logger.info(f"Generating {format} report from {results_path}")
    
    # Load results
    import json
    with open(results_path, "r") as f:
        results = json.load(f)
    
    # Generate report based on format
    if format == "html":
        report_path = generate_html_report(results, output_path, template_path)
    elif format == "pdf":
        # PDF generation would be implemented here
        logger.error("PDF report generation not yet implemented")
        raise NotImplementedError("PDF report generation not yet implemented")
    elif format == "md":
        # Markdown generation would be implemented here
        logger.error("Markdown report generation not yet implemented")
        raise NotImplementedError("Markdown report generation not yet implemented")
    else:
        logger.error(f"Unsupported report format: {format}")
        raise ValueError(f"Unsupported report format: {format}")
    
    logger.info(f"Report generated and saved to {report_path}")
    return report_path


def profile_data(file_path: str,
                sample_size: Optional[int] = None,
                sheet_name: Optional[str] = None,
                output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Profile a dataset.
    
    Args:
        file_path: Path to the data file
        sample_size: Number of rows to sample (0 for all)
        sheet_name: Sheet name for Excel files
        output_path: Optional path to save results
        
    Returns:
        Profiling results
    """
    from sage.data.profiler import profile_dataframe
    
    logger.info(f"Starting data profiling of {file_path}")
    start_time = time.time()
    
    # Load data
    logger.info("Loading data...")
    df = load_data(file_path, sheet_name=sheet_name)
    
    # Apply sampling if requested
    if sample_size and 0 < sample_size < len(df):
        df = df.sample(sample_size, random_state=42)
        logger.info(f"Sampled {sample_size} rows from dataset")
    
    logger.info(f"Profiling data with {len(df)} rows and {len(df.columns)} columns")
    
    # Profile the data
    profile_results = profile_dataframe(df)
    
    # Add metadata
    elapsed_time = time.time() - start_time
    profile_results["metadata"] = {
        "file_path": file_path,
        "rows": len(df),
        "columns": len(df.columns),
        "profiling_time": round(elapsed_time, 2)
    }
    
    logger.info(f"Profiling completed in {elapsed_time:.2f} seconds")
    
    # Save results if output path provided
    if output_path:
        import json
        with open(output_path, "w") as f:
            json.dump(profile_results, f, indent=2)
        logger.info(f"Profiling results saved to {output_path}")
    
    # Print summary to console
    print_profile_summary(profile_results)
    
    return profile_results


def print_profile_summary(profile_results: Dict[str, Any]) -> None:
    """
    Print a summary of profiling results to the console.
    
    Args:
        profile_results: Profiling results
    """
    print_banner("SAGE Data Profile Summary")
    
    metadata = profile_results.get("metadata", {})
    print(f"File: {metadata.get('file_path', 'Unknown')}")
    print(f"Rows: {metadata.get('rows', 0):,}")
    print(f"Columns: {metadata.get('columns', 0):,}")
    print(f"Time taken: {metadata.get('profiling_time', 0):.2f} seconds")
    print()
    
    # Column summary
    columns = profile_results.get("columns", {})
    if columns:
        print_banner("Column Summary")
        
        # Prepare data for table
        table_data = []
        for col_name, col_info in columns.items():
            col_type = col_info.get("type_category", "Unknown")
            completeness = col_info.get("completeness", 0) * 100
            unique_values = col_info.get("unique_count", 0)
            
            table_data.append({
                "Column": col_name,
                "Type": col_type.title(),
                "Completeness": f"{completeness:.1f}%",
                "Unique Values": f"{unique_values:,}"
            })
        
        print_table(table_data)


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    # Set up logging
    setup_logging(args.verbose if hasattr(args, "verbose") else False)
    
    try:
        if args.command == "assess":
            # Run assessment
            results = run_assessment(
                args.file,
                config_path=args.config,
                metrics=args.metrics,
                sheet_name=args.sheet,
                output_path=args.output
            )
            
            # Print summary to console
            if not args.output:
                print_result(results)
                
        elif args.command == "report":
            # Generate report
            report_path = generate_report(
                args.results,
                args.output,
                format=args.format,
                template_path=args.template
            )
            print(f"Report generated: {report_path}")
            
        elif args.command == "profile":
            # Profile data
            profile_data(
                args.file,
                sample_size=args.sample,
                sheet_name=args.sheet,
                output_path=args.output
            )
            
        elif args.command == "version":
            # Show version
            from sage import __version__
            print(f"SAGE version {__version__}")
            
        else:
            # No command or unsupported command
            logger.error("No command specified. Use --help for usage information.")
            return 1
            
        return 0  # Success
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if hasattr(args, "verbose") and args.verbose:
            import traceback
            traceback.print_exc()
        return 1  # Failure


if __name__ == "__main__":
    sys.exit(main())
