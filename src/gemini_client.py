import logging
import google.generativeai as genai
from typing import Dict, Optional

class GeminiClient:
    def __init__(self, api_key: str):
        """
        Initialize Gemini AI client.
        
        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        self.client = None
        self.modle = None
        self.setup_logging()


    def setup_logging(self):
        """Configure logging for the Gemini client."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GeminiClient')

    def connect(self) -> bool:
        """Establish connection to Gemini API."""
        try:
            
            genai.configure(api_key=self.api_key)
            self.modle = genai.GenerativeModel("gemini-1.5-flash")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Gemini API: {str(e)}")
            return False

    def analyze_table_schema_data(self, table_schema) -> Optional[Dict]:
        """
        Analyze IP data using Gemini AI.
        
        Args:
            ip_data: Dictionary containing IP information from Censys
            
        Returns:
            Dictionary containing AI analysis results
        """
        try:

            prompt = f"""
            You are a Data protection and privacy expert specializing in classifying and categorizing data being collected in databases.
            
            INPUT DATA IN PYTHON LIST FORMAT:
            {table_schema}

            ANALYSIS REQUIREMENTS:
            Provide a privacy and terms of use assessment of each colums and all columns in the INPUT DATA above in the following strict format for each column:

            Column: <name of column>
            Description: <description of the column maximum 15 words. no special characters>
            Type: <Required or Optional>
            Collection method: <Determine if the value in the column is USER PROVIDED or USAGE GENERATED or SET BY SYSTEM or THRIRD PARTY or OTHER>
            Gathered from: <Determine if the data is collected from ALL or VISITORS or REGISTRED USERS or THIRD PARTY or OTHER>
            Primary Purpose: <single line description maximum 20 words. no special characters><.>
            Legal basis: <10 words describing what the legal basis would be for collecting the information>
            <new line>

            CRITICAL FORMAT RULES:
            1. Do not use any commas periods or special characters
            2. Each field must be on a new line
            3. Use exact field names as shown above
            4. Keep all responses within specified word limits
            5. Maintain consistent capitalization of field names
            6. Use hyphens instead of commas or periods for separation
            7. Ensure each field has exactly one colon followed by a space
            8. Do not include any additional formatting or explanations

            ANALYSIS GUIDELINES:
            - Base your column description on:
            * Known tables from common CMS and LMS.
            * Other Columns you see that might be in relation.
            - Base your legal basis on:
            * GDPR
            * POPI Act South Africa

            Your response must be directly parseable by the following format indicators:
            - Line starts with field name followed by colon
            - Single space after colon
            - No line breaks within fields
            - No extra whitespace
            - No additional formatting
            """
            response = self.modle.generate_content(prompt)
            analysis = response.text

            # Parse the analysis into structured fields
            analysis_dict = self._parse_analysis(analysis)
        

            return analysis_dict

        except Exception as e:
            self.logger.error(f"Error analyzing file {table_schema}")
            return None

    def _parse_analysis(self, analysis: str) -> Dict:
        """
        Parse Gemini's analysis into structured fields.
        
        Args:
            analysis: Raw analysis text from Gemini
            
        Returns:
            Dictionary containing parsed analysis fields
        """
        # Initialize default values
        parsed = {
            'column': '',
            'description': '',
            'type': '',
            'collection': '',
            'gathered-from': "",
            'purpose': '',
            'legal-basis': ''
        }

        parsed_dictionaries = []

        # Simple parsing based on field markers
        current_field = None
        for line in analysis.split('\n'):
            line = line.strip()
            lower_line = line.lower()

            if 'column' in lower_line and ':' in line:
                current_field = 'column'
                parsed[current_field] = line.split(':', 1)[1].strip()
            elif 'description' in lower_line and ':' in line:
                current_field = 'description'
                parsed[current_field] = line.split(':', 1)[1].strip()
            elif 'type' in lower_line and ':' in line:
                current_field = 'type'
                parsed[current_field] = line.split(':', 1)[1].strip()
            elif 'collection' in lower_line and ':' in line:
                current_field = 'collection'
                parsed[current_field] = line.split(':', 1)[1].strip()
            elif 'gathered' in lower_line and ':' in line:
                current_field = 'gathered-from'
                parsed[current_field] = line.split(':', 1)[1].strip()
            elif 'purpose' in lower_line and ':' in line:
                current_field = 'purpose'
                parsed[current_field] = line.split(':', 1)[1].strip()
            elif 'legal basis' in lower_line and ':' in line:
                current_field = 'legal-basis'
                parsed[current_field] = line.split(':', 1)[1].strip()
                parsed_dictionaries.append(parsed)
                parsed = {
                    'column': '',
                    'description': '',
                    'type': '',
                    'collection': '',
                    'gathered-from': "",
                    'purpose': '',
                    'legal-basis': ''
                }


        return parsed_dictionaries