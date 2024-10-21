# DB Privacy Analyzer

An automated tool that analyzes database schemas to identify data collection patterns and generates privacy-aware documentation and terms of service.

## 🎯 Purpose

This tool helps organizations:
- Automatically scan and analyze database schemas
- Identify types of data being collected
- Generate data collection insights using AI
- Create privacy-focused documentation
- Assist in terms of service generation

## 🏗️ Architecture

The project consists of four main modules:
1. **Database Handler**: Connects to databases and extracts schema information
2. **AI Processor**: Analyzes schema data and classifies data types (pre-developed)
3. **Spreadsheet Generator**: Creates detailed Excel reports of findings
4. **Documentation Generator**: Assists in ToS generation (future development)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL Connector
- pandas
- openpyxl

### Installation
```bash
git clone https://github.com/yourusername/db-privacy-analyzer.git
cd db-privacy-analyzer
pip install -r requirements.txt
```

### Configuration
Create a `.env` file with your database and gemini credentials:
```env
DB_HOST=your_host
DB_USER=your_username
DB_PASSWORD=your_password
DB_DATABASE=your_database
GEMINI_API_KEY=your-gemini-api-key
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔒 Security Note

This tool is designed to handle sensitive database information. Always ensure proper security measures are in place when using it in production environments.