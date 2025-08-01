# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a conversation analytics experiment project that uses DuckDB and MinIO for data storage and analysis. The project is focused on storing and analyzing conversational interactions between users and AI systems.

## Development Commands

This project uses Poetry for Python dependency management:

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run setup script (after starting docker-compose)
python setup.py

# Example query script
python query_example.py

# AI-powered natural language querying (CLI)
export OPENAI_API_KEY="your-openai-key"  # OR
export GOOGLE_AI_API_KEY="your-google-key"
python query_chat.py

# Test the SQL agent
python test_agent.py
```

## Infrastructure

The project uses Docker Compose to run the required infrastructure:

```bash
# Start MinIO object storage and Iceberg REST catalog
docker-compose up -d

# Stop services
docker-compose down
```

### Services:
- **MinIO**: Object storage service running on ports 9000 (API) and 9001 (console)
  - Default credentials: minioadmin/minioadmin123
  - Used for storing data files accessed by DuckDB

## Data Architecture

The project uses DuckDB with S3 integration for data storage and analysis:

### Table Schema 
- **conversation_entry**: Main table storing conversational interactions
  - Stored as partitioned Parquet files in S3: `s3://convo/tables/conversation_entry/`
  - Partitioned by `date` and `hour` for efficient querying
  - Includes nested `sources` array for RAG-based search metadata
  - Query with DuckDB using S3 paths

### Key Fields:
- `entry_id`: Unique identifier combining sessionId and interactionId
- `session_id`: Client-set session identifier
- `interaction_id`: Sequential interaction ordering within sessions
- `question`/`answer`: The conversational content with timestamps
- `sources`: Array of RAG sources with names and relevance scores
- Location/organizational hierarchy fields (location_id, region_id, group_id, district_id)

## Storage Configuration

- S3 bucket: `convo` (created in MinIO)  
- Table data stored as Parquet files in S3: `s3://convo/tables/`
- DuckDB configured with S3 integration for MinIO
- All timestamps stored with timezone information
- Dates/hours in Central Time
- No local database file - all data in S3

## AI-Powered Natural Language Querying

The project includes an AI agent that converts natural language questions into DuckDB SQL queries:

### Features:
- **Natural Language Processing**: Ask questions in plain English
- **Multiple AI Providers**: Supports both OpenAI GPT-4 and Google Gemini
- **Schema-Aware**: Understands table structure and generates appropriate queries
- **Rich CLI Interface**: Beautiful terminal interface with formatted tables and markdown
- **Debug Mode**: Optional SQL query display for troubleshooting
- **Follow-up Queries**: Ask contextual follow-up questions that reference previous results

### Example Questions:
- "How many conversations are there?"
- "Show me conversations by date"
- "What are the most common user actions?"
- "Which sessions had more than 3 interactions?"
- "What questions were asked about inventory?"

### Usage:
```bash
# Set your AI API key
export OPENAI_API_KEY="your-key-here"  # OR
export GOOGLE_AI_API_KEY="your-key-here"

# Start interactive CLI
python query_chat.py

# Available commands in CLI:
# - Type your question and press Enter
# - 'help' for example questions
# - 'debug on/off' to show/hide SQL queries
# - 'clear' to clear conversation context
# - 'quit' or 'exit' to quit

# Follow-up query examples:
# 1. "Show me conversations from yesterday"  
# 2. "Show me the ones that contain 'Sorry'" (references previous results)
# 3. "Filter those by store 1001" (further refines previous results)
```

## Manual SQL Querying

```python
# Query data from S3 with DuckDB
conn = duckdb.connect(':memory:')
conn.execute("INSTALL httpfs; LOAD httpfs;")
# Configure S3 settings...
result = conn.execute("SELECT * FROM 's3://convo/tables/conversation_entry/**/*.parquet'")
```