"""
Database grader implementation for SAGE.

This module provides functionality to assess data quality in database tables
using configurable metrics and scoring criteria.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Set
import datetime
import sqlalchemy
import pandas as pd
import re

from sage.graders.base_grader import BaseGrader

# Set up logger
logger = logging.getLogger("sage.graders.database")


class DatabaseGrader(BaseGrader):
    """
    Data quality grader for database sources.
    
    Connects to database tables and applies metrics to assess data quality.
    Supports multiple database types and SQL-specific features.
    """
    
    def __init__(self, name: str = None):
        """
        Initialize a database grader.
        
        Args:
            name: Human-readable name for this grader
        """
        super().__init__(name)
        
        # Database-specific properties
        self.engine = None           # SQLAlchemy engine
        self.connection = None       # SQLAlchemy connection
        self.inspector = None        # SQLAlchemy inspector
        self.db_type = None          # Type of database (postgresql, mysql, etc.)
        self.active_schema = None    # Currently selected schema
        self.active_table = None     # Currently selected table
        
        logger.debug(f"Initialized database grader: {self.name}")
    
    def connect(self, source: Union[str, sqlalchemy.engine.Engine]) -> bool:
        """
        Connect to a database.
        
        Args:
            source: Either:
                   - Connection string (e.g., "postgresql://user:pass@localhost/db")
                   - SQLAlchemy engine
                   
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            ValueError: If source type is not supported
            sqlalchemy.exc.SQLAlchemyError: If connection fails
        """
        try:
            # Reset state
            self.engine = None
            self.connection = None
            self.inspector = None
            self.db_type = None
            self.active_schema = None
            self.active_table = None
            self.is_connected = False
            
            if isinstance(source, str):
                # It's a connection string
                logger.info(f"Connecting to database: {self._mask_connection_string(source)}")
                self.engine = sqlalchemy.create_engine(source)
                
            elif isinstance(source, sqlalchemy.engine.Engine):
                # It's an SQLAlchemy engine
                logger.info("Connecting using provided SQLAlchemy engine")
                self.engine = source
                
            else:
                raise ValueError("Source must be a connection string or SQLAlchemy engine")
            
            # Establish connection and create inspector
            self.connection = self.engine.connect()
            self.inspector = sqlalchemy.inspect(self.engine)
            
            # Determine database type
            dialect = self.engine.dialect.name
            self.db_type = dialect.lower()
            
            # Set default schema based on database type
            if self.db_type == 'postgresql':
                self.active_schema = 'public'
            elif self.db_type == 'mysql':
                # MySQL uses schemas as databases
                # The active schema should be the database name from the connection
                url = self.engine.url
                self.active_schema = url.database
            
            # Mark connection as successful
            self.source = source
            self.is_connected = True
            
            logger.info(f"Connected to {self.db_type} database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            # Re-raise so the caller can handle it
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.debug("Closed database connection")
        
        self.is_connected = False
    
    def get_available_schemas(self) -> List[str]:
        """
        Get list of available schemas.
        
        Returns:
            List of schema names
        """
        if not self.is_connected or not self.inspector:
            return []
        
        try:
            return self.inspector.get_schema_names()
        except Exception as e:
            logger.error(f"Error getting schemas: {str(e)}")
            return []
    
    def get_available_tables(self, schema: Optional[str] = None) -> List[str]:
        """
        Get list of available tables in a schema.
        
        Args:
            schema: Schema to list tables from (uses active schema if None)
            
        Returns:
            List of table names
        """
        if not self.is_connected or not self.inspector:
            return []
        
        use_schema = schema or self.active_schema
        
        try:
            return self.inspector.get_table_names(schema=use_schema)
        except Exception as e:
            logger.error(f"Error getting tables for schema '{use_schema}': {str(e)}")
            return []
    
    def set_active_schema(self, schema: str) -> bool:
        """
        Set the active schema for database operations.
        
        Args:
            schema: Schema name to set as active
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If schema doesn't exist
        """
        if not self.is_connected:
            raise ValueError("Not connected to a database")
        
        # Get available schemas
        available_schemas = self.get_available_schemas()
        
        if schema not in available_schemas:
            raise ValueError(f"Schema '{schema}' does not exist")
        
        self.active_schema = schema
        logger.debug(f"Set active schema to: {schema}")
        return True
    
    def set_active_table(self, table: str, schema: Optional[str] = None) -> bool:
        """
        Set the active table for grading operations.
        
        Args:
            table: Table name to set as active
            schema: Schema containing the table (uses active schema if None)
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If table doesn't exist in the schema
        """
        if not self.is_connected:
            raise ValueError("Not connected to a database")
        
        # Use provided schema or default to active schema
        use_schema = schema or self.active_schema
        
        # Get available tables in the schema
        available_tables = self.get_available_tables(use_schema)
        
        if table not in available_tables:
            raise ValueError(f"Table '{table}' does not exist in schema '{use_schema}'")
        
        self.active_schema = use_schema
        self.active_table = table
        logger.debug(f"Set active table to: {use_schema}.{table}")
        return True
    
    def get_table_info(self, table: Optional[str] = None, schema: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a table.
        
        Args:
            table: Table name (uses active table if None)
            schema: Schema name (uses active schema if None)
            
        Returns:
            Dictionary with table metadata
        """
        if not self.is_connected or not self.inspector:
            raise ValueError("Not connected to a database")
        
        use_table = table or self.active_table
        use_schema = schema or self.active_schema
        
        if not use_table:
            raise ValueError("No active table selected")
        
        # Get column information
        try:
            columns = {}
            col_info = self.inspector.get_columns(use_table, schema=use_schema)
            
            for col in col_info:
                col_name = col['name']
                columns[col_name] = {
                    "type": str(col['type']),
                    "nullable": col.get('nullable', True),
                    "default": col.get('default', None),
                    "primary_key": False  # Will be updated below if it's a PK
                }
            
            # Get primary key information
            try:
                pk_info = self.inspector.get_pk_constraint(use_table, schema=use_schema)
                pk_columns = pk_info.get('constrained_columns', [])
                
                for col in pk_columns:
                    if col in columns:
                        columns[col]['primary_key'] = True
            except Exception as e:
                logger.warning(f"Could not get primary key information: {str(e)}")
            
            # Get row count (this might be slow for large tables)
            row_count = None
            try:
                query = f"SELECT COUNT(*) FROM {use_schema}.{use_table}" if use_schema else f"SELECT COUNT(*) FROM {use_table}"
                result = self.connection.execute(sqlalchemy.text(query))
                row_count = result.scalar()
            except Exception as e:
                logger.warning(f"Could not get row count: {str(e)}")
            
            return {
                "schema": use_schema,
                "table": use_table,
                "row_count": row_count,
                "column_count": len(columns),
                "columns": columns
            }
            
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the results as a DataFrame.
        
        Args:
            query: SQL query to execute
            
        Returns:
            DataFrame with query results
            
        Raises:
            ValueError: If not connected to a database
            sqlalchemy.exc.SQLAlchemyError: If query execution fails
        """
        if not self.is_connected or not self.connection:
            raise ValueError("Not connected to a database")
        
        try:
            return pd.read_sql(query, self.connection)
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def grade(self, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run metrics against the active database table.
        
        Args:
            metrics: Optional list of metric names to run (runs all if None)
            
        Returns:
            Dictionary of results keyed by metric name
            
        Raises:
            ValueError: If no metrics are configured or no database is connected
                        or no active table is selected
        """
        if not self.active_table:
            raise ValueError("No active table selected. Call set_active_table() first.")
        
        # Get the metrics to run
        metrics_to_run = self._prepare_for_grading(metrics)
        
        if not metrics_to_run:
            logger.warning("No metrics to run - returning empty results")
            return {}
        
        # Get the table data as a DataFrame for the metrics to process
        # This might not be efficient for very large tables, but works for now
        query = f"SELECT * FROM {self.active_schema}.{self.active_table}" if self.active_schema else f"SELECT * FROM {self.active_table}"
        try:
            logger.info(f"Loading data from table {self.active_schema}.{self.active_table}" if self.active_schema else f"Loading data from table {self.active_table}")
            df = self.execute_query(query)
            logger.debug(f"Loaded {len(df)} rows from table")
        except Exception as e:
            logger.error(f"Failed to load table data: {str(e)}")
            raise ValueError(f"Could not load data from table: {str(e)}")
        
        # Run each metric and collect results
        results = {}
        start_time = datetime.datetime.now()
        
        for name, metric in metrics_to_run:
            try:
                # Most metrics will have a common evaluate() interface
                metric_result = metric.evaluate(df)
                results[name] = metric_result
                logger.debug(f"Metric '{name}' completed with score: {metric_result.get('score', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Error running metric '{name}': {str(e)}")
                # Store the error but don't fail the whole grading process
                results[name] = {
                    "error": str(e),
                    "status": "failed",
                    "score": 0
                }
        
        # Calculate timing information
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Get table metadata for the report
        table_info = self.get_table_info()
        
        # Enrich results with metadata
        results_with_meta = {
            "metrics": results,
            "metadata": {
                "database": {
                    "db_type": self.db_type,
                    "schema": self.active_schema,
                    "table": self.active_table,
                    "row_count": table_info.get('row_count'),
                    "column_count": table_info.get('column_count'),
                    "columns": list(table_info.get('columns', {}).keys())
                },
                "timing": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration
                }
            }
        }
        
        # Store results
        self._store_results(results)
        
        logger.info(f"Database grading completed in {duration:.2f} seconds with {len(results)} metrics")
        
        return results_with_meta
    
    def get_active_data(self) -> pd.DataFrame:
        """
        Get the active table data as a DataFrame.
        
        Returns:
            DataFrame of the active table or None if not connected or no active table
        """
        if not self.is_connected or not self.active_table:
            return None
            
        query = f"SELECT * FROM {self.active_schema}.{self.active_table}" if self.active_schema else f"SELECT * FROM {self.active_table}"
        try:
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Error getting active data: {str(e)}")
            return None
    
    def _mask_connection_string(self, conn_string: str) -> str:
        """
        Mask sensitive information in a connection string for logging.
        
        Args:
            conn_string: Database connection string
            
        Returns:
            Connection string with password masked
        """
        # Match user:password@ pattern commonly found in connection strings
        pattern = r'(//\w+:)([^@]+)(@)'
        return re.sub(pattern, r'\1******\3', conn_string)
