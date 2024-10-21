# src/database/connector.py

import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class DatabaseConfig:
    host: str
    user: str
    password: str
    database: str
    port: int = 3306

class DatabaseConnector:
    def __init__(self, database_username:str, database_password:str, database_hostname:str, database_name:str, port=3306):
        """Initialize database connector with either config file or direct parameters."""
        self.database_username = database_username
        self.database_password = database_password
        self.database_hostname = database_hostname
        self.database_name = database_name
        self.port = port
        self._connection = None
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for the database operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)


    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        try:
            if not self._connection or not self._connection.is_connected():
                self._connection = mysql.connector.connect(
                    host=self.database_hostname,
                    user=self.database_username,
                    password=self.database_password,
                    database=self.database_name,
                    port=self.port
                )
            yield self._connection
        except Error as e:
            self.logger.error(f"Error connecting to MySQL: {e}")
            raise
        finally:
            if self._connection and self._connection.is_connected():
                self._connection.close()

"""
# Usage example:
if __name__ == "__main__":
    # Initialize with config file
    db_connector = DatabaseConnector("config/config.yaml")
    analyzer = SchemaAnalyzer(db_connector)
    
    # Get schema information
    schema_info = analyzer.analyze_schema()
    
    # Print some basic information
    print(f"Database: {schema_info['database_name']}")
    print(f"Number of tables: {len(schema_info['tables'])}")
    for table in schema_info['tables']:
        print(f"\nTable: {table['table_name']}")
        print(f"Number of columns: {len(table['columns'])}")
        print(f"Number of relationships: {len(table['relationships'])}")

"""