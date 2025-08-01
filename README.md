# Conversation Analytics Platform

A modern data analytics platform for analyzing conversational AI interactions using DuckDB and MinIO. This project provides tools for storing, querying, and analyzing conversation data with both traditional SQL and AI-powered natural language queries.

## Architecture

- **Storage**: MinIO S3-compatible object storage
- **Analytics**: DuckDB for high-performance analytical queries
- **Data Format**: Partitioned Parquet files for optimal query performance
- **AI Integration**: Natural language to SQL conversion using OpenAI GPT-4 or Google Gemini

## Features

- 🚀 **High Performance**: DuckDB with S3 integration for fast analytical queries
- 📊 **Partitioned Storage**: Data partitioned by date/hour for efficient filtering
- 🤖 **AI-Powered Querying**: Ask questions in natural language, get SQL results
- 🏪 **Realistic Sample Data**: 5000+ retail operational conversations with authentic Q&A patterns
- 🔄 **Flexible Data Management**: Easy setup, data generation, and cleanup tools

## Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Poetry (recommended) or pip

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd convo

# Install dependencies
poetry install
# OR using pip
pip install -r requirements.txt

# Copy configuration template
cp .env.example .env
# Edit .env with your settings (API keys, etc.)
```

### 2. Start Infrastructure

```bash
# Start MinIO object storage
docker-compose up -d

# Verify MinIO is running
curl http://localhost:9000/minio/health/live
```

### 3. Generate Sample Data

```bash
# Create tables and generate 5000 sample conversations
python setup.py -a
```

This creates:
- **5000 conversations** with 1-8 interactions each (~15,000+ total entries)
- **Realistic retail scenarios**: Inventory, customer service, POS, safety, HR, seasonal
- **25% failure rate**: "Sorry, I can't answer that" responses
- **3-month timespan**: Data distributed across the past 90 days
- **Proper partitioning**: Organized by date and hour for efficient queries

### 4. Verify Setup

```bash
# Test basic functionality
python test_agent.py

# Run sample queries
python query_example.py
```

## Data Schema

### Conversation Entry Table

| Column | Type | Description |
|--------|------|-------------|
| `entry_id` | VARCHAR | Unique identifier (session_id + interaction_id) |
| `session_id` | VARCHAR | Groups related interactions into conversations |
| `interaction_id` | INTEGER | Sequential number within a session (1, 2, 3...) |
| `date` | DATE | Date of the conversation |
| `hour` | INTEGER | Hour of day (0-23) |
| `question` | VARCHAR | User's question |
| `question_created` | TIMESTAMPTZ | Question timestamp |
| `answer` | VARCHAR | AI response |
| `answer_created` | TIMESTAMPTZ | Response timestamp |
| `action` | VARCHAR | Action category (general, inventory, customer_service, etc.) |
| `user_id` | VARCHAR | User identifier |
| `location_id` | INTEGER | Store location (1001-1499) |
| `region_id` | INTEGER | Regional grouping (100-149) |
| `group_id` | INTEGER | Group identifier (10-24) |
| `district_id` | INTEGER | District identifier (1-14) |
| `user_roles` | VARCHAR[] | User roles array |
| `sources` | STRUCT[] | RAG sources with relevance scores |

**Storage**: `s3://convo/tables/conversation_entry/` (partitioned by date/hour)

## Usage Examples

### Traditional SQL Queries

```python
import duckdb

# Connect and configure
conn = duckdb.connect(':memory:')
conn.execute("INSTALL httpfs; LOAD httpfs;")
conn.execute("""
    SET s3_endpoint = 'localhost:9000';
    SET s3_access_key_id = 'minioadmin';
    SET s3_secret_access_key = 'minioadmin123';
    SET s3_use_ssl = false;
    SET s3_url_style = 'path';
""")

# Query the data
result = conn.execute("""
    SELECT 
        date,
        COUNT(*) as conversations,
        AVG(interaction_id) as avg_interactions
    FROM 's3://convo/tables/conversation_entry/**/*.parquet' 
    GROUP BY date 
    ORDER BY date
""").fetchall()
```

### AI-Powered Natural Language Queries

```bash
# Configure your API keys in .env file:
# OPENAI_API_KEY=your-openai-api-key
# GOOGLE_AI_API_KEY=your-google-ai-api-key
# DEFAULT_AI_PROVIDER=openai

# Launch web interface
python query_chat.py
# Opens automatically at http://localhost:7860
```

**Web Interface Features:**
- 🌐 **Clean Web UI**: User-friendly interface with real-time results
- 📊 **Markdown Rendering**: Results displayed as formatted tables and charts
- 🔍 **SQL Debug Mode**: View generated SQL queries when `DEBUG_MODE=True`
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🔄 **Real-time Processing**: Instant query execution with loading indicators

**Example Queries:**
- "How many conversations are there?"
- "What are the busiest hours for conversations?"
- "Show me conversations by date"
- "How many conversations couldn't be answered?"
- "What are the most common inventory questions?"

### Alternative Query Methods

```bash
# Basic querying examples (command line)
python query_example.py

# Test the AI agent
python test_agent.py

# Web interface (recommended)
python query_chat.py
```

## Management Commands

### Setup Commands
```bash
# Basic setup (table structure only)
python setup.py

# Create sample data (recommended)
python setup.py -a

# Delete all data
python setup.py -d
```

### Data Operations
```bash
# View MinIO console
open http://localhost:9001
# Login: minioadmin / minioadmin123

# Stop services
docker-compose down

# Clean restart
docker-compose down -v  # Remove volumes
docker-compose up -d
python setup.py -a      # Recreate data
```

## Development

### Project Structure
```
convo/
├── setup.py              # Main setup and data generation
├── sql_agent.py           # AI-powered SQL generation
├── query_chat.py          # Interactive natural language interface
├── query_example.py       # Sample query demonstrations
├── test_agent.py          # Testing utilities
├── docker-compose.yml     # MinIO infrastructure
├── pyproject.toml         # Python dependencies
└── tables.sql            # Original table schema reference
```

### Adding Custom Data

To add your own conversation data:

1. **Follow the schema**: Match the conversation_entry table structure
2. **Maintain partitioning**: Include proper date/hour values
3. **Use DuckDB COPY**: Export data to S3 with partitioning

```python
# Example: Custom data insertion
conn.execute("""
    COPY your_custom_table 
    TO 's3://convo/tables/conversation_entry/' 
    (FORMAT PARQUET, PARTITION_BY (date, hour), OVERWRITE_OR_IGNORE)
""")
```

### Testing

```bash
# Run all tests
python test_agent.py

# Test specific components
python -c "from sql_agent import SQLAgent; agent = SQLAgent(); print('Agent initialized')"
```

## Performance Notes

- **Partitioning**: Queries filtering by date/hour are highly optimized
- **Columnar Storage**: Parquet format enables efficient column-based analytics
- **S3 Integration**: DuckDB's httpfs extension provides seamless S3 querying
- **Memory Efficiency**: In-memory DuckDB connections minimize resource usage

## Troubleshooting

### Common Issues

**MinIO Connection Failed**
```bash
# Check if MinIO is running
docker-compose ps
curl http://localhost:9000/minio/health/live
```

**Missing Dependencies**
```bash
# Install missing modules
poetry install
# OR
pip install pytz duckdb boto3 google-generativeai openai
```

**S3 Permission Errors**
```bash
# Restart MinIO with clean state
docker-compose down -v
docker-compose up -d
```

**AI Query Errors**
```bash
# Check your .env file contains API keys
cat .env | grep API_KEY

# Verify environment variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('Google:', bool(os.getenv('GOOGLE_AI_API_KEY')))"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is for experimental and educational purposes.