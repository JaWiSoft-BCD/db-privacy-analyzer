import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from config import ConfigHandler
from db_handler import DatabaseConnector
from db_schema_analyzer import SchemaAnalyzer
from sheet_handler import ExcelGenerator
from gemini_client import GeminiClient  # Your existing AI module

class PrivacyAnalyzer:
    def __init__(self):
        """Initialize the Privacy Analyzer with configuration."""
        self._setup_logging()
        self.config = self._load_config()
        self._setup_components()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            configuration = ConfigHandler()
            credentials = configuration.get_credentials()
            return credentials
        except Exception as e:
            raise ValueError(f"Error loading config file: {str(e)}")

    def _setup_logging(self):
        """Configure logging for the application."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"privacy_analyzer_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _setup_components(self):
        """Initialize all component classes."""
        try:
            database_name = self.config['DB_DATABASE']
            database_user = self.config['DB_USER']
            database_pw = self.config['DB_PASSWORD']
            database_host = self.config['DB_HOST']
            self.db_connector = DatabaseConnector(database_user, database_pw, database_host, database_name)
            self.schema_analyzer = SchemaAnalyzer(self.db_connector)
            self.ai_classifier = GeminiClient(api_key=self.config['GEMINI_API_KEY'])
            self.ai_classifier.connect()
            self.excel_generator = ExcelGenerator()
        except Exception as e:
            self.logger.error(f"Error setting up components: {str(e)}")
            raise

    def analyze_database(self, database_name: Optional[str] = None) -> str:
        """
        Perform complete database analysis and generate report.
        Returns the path to the generated report.
        """
        try:
            self.logger.info("Starting database analysis")
            
            # Use provided database name or from config
            # db_name = database_name or self.config['database']['database']
            
            # Step 1: Extract schema information
            self.logger.info("Extracting database schema")
            schema_info = self.schema_analyzer.analyze_schema()
            
            # Step 2: Process schema with AI
            self.logger.info("Analyzing schema with AI classifier")
            ai_analysis = self._process_schema_with_ai(schema_info)
            
            # Step 3: Generate Excel report
            self.logger.info("Generating Excel report")
            report_path = self.excel_generator.generate_report(ai_analysis, self.db_connector.database_name)
            
            #self.logger.info(f"Analysis completed successfully. Report generated at: {report_path}")
            # return report_path
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}")
            raise

    def _process_schema_with_ai(self, schema_info: Dict[str, Any]) -> list:
        """Process schema information with AI classifier."""
        ai_results = []
        
        for table in schema_info['tables']:
            table_name = table['table_name']
            
            # Get AI classification
            classification = self.ai_classifier.analyze_table_schema_data(table)
            
            # Add to results
            if classification:
                ai_results.append({
                    "table_name": table_name,
                    "column_report": classification
                })
            time.sleep(3.9)
        
        return ai_results

    def _find_relationships(self, relationships: list, column_name: str) -> list:
        """Find relationships for a specific column."""
        return [rel for rel in relationships if rel['column_name'] == column_name]

def main():
    """Main entry point for the application."""
    try:
        analyzer = PrivacyAnalyzer()
        
        report_path = analyzer.analyze_database()
        print(f"\nAnalysis complete! Report generated at: {report_path}")
        
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()