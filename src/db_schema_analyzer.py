from typing import Dict, List, Any
from db_handler import DatabaseConnector
import logging

class SchemaAnalyzer:
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector
        self.logger = logging.getLogger(__name__)

    def analyze_schema(self) -> Dict[str, Any]:
        """
        Analyze the database schema and return a structured dictionary of the findings.
        """
        schema_info = {
            "database_name": self.db_connector.database_name,
            "tables": self._get_tables_info()
        }
        return schema_info

    def _get_tables_info(self) -> List[Dict[str, Any]]:
        """Get detailed information about all tables in the database."""
        tables_info = []
        
        with self.db_connector.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            # Get all tables
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s
            """, (self.db_connector.database_name,))
            
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table['TABLE_NAME']
                table_info = {
                    "table_name": table_name,
                    "columns": self._get_columns_info(cursor, table_name),
                    "relationships": self._get_relationships(cursor, table_name),
                    "metadata": self._get_table_metadata(cursor, table_name)
                }
                tables_info.append(table_info)
                
        return tables_info

    def _get_columns_info(self, cursor, table_name: str) -> List[Dict[str, Any]]:
        """Get detailed information about columns in a table."""
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_KEY,
                EXTRA,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (self.db_connector.database_name, table_name))
        
        columns = []
        for column in cursor.fetchall():
            column_info = {
                "name": column['COLUMN_NAME'],
                "data_type": column['DATA_TYPE'],
                "max_length": column['CHARACTER_MAXIMUM_LENGTH'],
                "is_nullable": column['IS_NULLABLE'] == 'YES',
                "default_value": column['COLUMN_DEFAULT'],
                "is_primary": column['COLUMN_KEY'] == 'PRI',
                "is_unique": column['COLUMN_KEY'] in ('UNI', 'PRI'),
                "auto_increment": 'auto_increment' in column['EXTRA'].lower(),
                "comment": column['COLUMN_COMMENT']
            }
            columns.append(column_info)
        
        return columns

    def _get_relationships(self, cursor, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key relationships for a table."""
        cursor.execute("""
            SELECT
                CONSTRAINT_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (self.db_connector.database_name, table_name))
        
        relationships = []
        for rel in cursor.fetchall():
            relationship = {
                "constraint_name": rel['CONSTRAINT_NAME'],
                "column_name": rel['COLUMN_NAME'],
                "referenced_table": rel['REFERENCED_TABLE_NAME'],
                "referenced_column": rel['REFERENCED_COLUMN_NAME']
            }
            relationships.append(relationship)
            
        return relationships

    def _get_table_metadata(self, cursor, table_name: str) -> Dict[str, Any]:
        """Get metadata about the table."""
        cursor.execute("""
            SELECT
                TABLE_COMMENT,
                ENGINE,
                ROW_FORMAT,
                CREATE_TIME,
                UPDATE_TIME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (self.db_connector.database_name, table_name))
        
        metadata = cursor.fetchone()
        return {
            "comment": metadata['TABLE_COMMENT'],
            "engine": metadata['ENGINE'],
            "row_format": metadata['ROW_FORMAT'],
            "created_at": metadata['CREATE_TIME'],
            "updated_at": metadata['UPDATE_TIME']
        }