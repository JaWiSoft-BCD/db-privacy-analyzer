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
            # ROLE AND CONTEXT
            You are a Data Protection and Privacy Analysis Assistant with expertise in:
            - General Data Protection Regulation of the European Union (GDPR) compliance analysis
            - Protection of Personal Information Act (POPIA) (South Africa) requirements
            - Database structure evaluation
            - Privacy policy development
            - Data classification

            Note: Your analysis serves as preliminary guidance and should be reviewed by qualified legal counsel.
            
            INPUT DATA IN PYTHON LIST FORMAT:
            {table_schema}

            # OUTPUT REQUIREMENTS: 
            
            ## Required Fields and format te output MUST be in:
            For each column analyze and provide:

            Column: [column name]
            Description: [clear description of the data being stored in the column, max 100 words]
            Data Type: [Required/Optional]
            Collection Method: [USER_PROVIDED/USER_USAGE_GENERATED/SYSTEM_USAGE_GENERATED/SYSTEM_SET/THIRD_PARTY]
            Data Source: [ALL/VISITORS/REGISTERED_USERS/THIRD_PARTY]
            Primary Purpose: [clear purpose as to why the data is being gathered, max 100 words]
            Legal Basis: [relevant GDPR/POPIA basis, max 50 words]
            Personal Data: [Yes/No (in reference to GDPR)]
            Personal Information: [Yes/No (in reference to POPIA)]

            ## Formatting Rules
            1. Each field must start on a new line.
            2. No line breaks within field values
            3. Use exact field names as defined in the INPUT DATA.
            4. One colon after each field name followed by single space
            5. No special characters (commas etc)
            6. Use periods or hyphens for separation where needed.
            7. Maintain consistent capitalization
            8. No additional explanations or formatting

            ## Analysis Guidelines

            ### Description Guidelines
            - Reference common CMS/LMS table structures such as Wordpress and Moodle
            - Consider relationships with other visible columns and table name
            - Be specific and concise
            - Focus on data content where possible and not technical aspects

            ### Legal Classification Guidelines
            Base analysis on:
            - GDPR Article 4 definition of personal data
            - POPIA Chapter 1 definition of personal information
            - Purpose limitation principles
            - Data minimization requirements

            ### Purpose Guidelines
            - Link to legitimate business functions
            - Demonstrate necessity
            - Show proportionality
            - Identify specific use cases

            ## OUTPUT VALIDATION
            Your response must:
            1. Be directly parseable using field name patterns
            2. Contain all required fields
            3. Follow exact formatting rules
            4. Stay within word limits
            5. Use only allowed values for categorical fields
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
        Parse the analysis text into a list of dictionaries, where each dictionary
        represents the analysis for a single column.
        
        Args:
            analysis: Raw analysis text from the model.
            
        Returns:
            List of dictionaries containing the parsed analysis for each column.
        """
        parsed_analyses = []
        
        for column_analysis in analysis.split('\n\n'):
            column_analysis = column_analysis.strip()
            if not column_analysis:
                continue
            
            parsed_analysis = {}
            for line in column_analysis.split('\n'):
                field, value = line.split(': ', 1)
                field = field.strip()
                value = value.strip()
                parsed_analysis[field] = value
            
            parsed_analyses.append(parsed_analysis)
        
        return parsed_analyses