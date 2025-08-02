# Conversation Analytics Platform

A modern, professionally-structured data analytics platform for analyzing conversational AI interactions. Built with DuckDB, MinIO, and FastAPI, this platform provides comprehensive tools for storing, querying, and analyzing conversation data with both traditional SQL and AI-powered natural language queries.

## 🚀 Features

- **🏗️ Professional Architecture**: Organized Python package structure with clear separation of concerns
- **📊 High Performance**: DuckDB with S3 integration for fast analytical queries on partitioned Parquet data
- **🤖 AI-Powered Querying**: Natural language to SQL conversion using OpenAI GPT-4 or Google Gemini
- **🌐 REST API**: Comprehensive FastAPI-based web service with interactive documentation
- **🔍 Database Views**: Pre-built analytical views for common queries with automatic AI integration
- **💻 Multiple Interfaces**: Interactive CLI, REST API, and programmatic access
- **🏪 Realistic Data**: 5000+ retail operational conversations with authentic Q&A patterns
- **🧪 Comprehensive Testing**: Full test suite with fixtures and integration tests

## 📁 Project Structure

```
convo/
├── src/convo/                  # Main Python package
│   ├── core/                   # Core business logic
│   │   ├── view_manager.py     # Database view management
│   │   └── sql_agent.py        # AI SQL generation
│   ├── api/                    # REST API components
│   │   ├── main.py             # FastAPI application
│   │   ├── models.py           # Pydantic request/response models
│   │   └── routes/             # API endpoints
│   │       ├── health.py       # Health check endpoints
│   │       ├── views.py        # Database view endpoints
│   │       └── query.py        # AI query endpoints
│   └── config/                 # Configuration management
│       └── settings.py         # Centralized settings
├── scripts/                    # Utility scripts
│   ├── setup.py               # Data setup and initialization
│   ├── manage_views.py        # View management CLI
│   └── start_api.py           # API server startup
├── cli/                       # Command-line interfaces
│   └── query_chat.py          # Interactive query CLI
├── examples/                  # Usage examples
├── tests/                     # Comprehensive test suite
├── data/                      # Data files and configurations
└── docs/                      # Documentation
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Poetry (recommended) or pip

### Super Quick Start (Using Makefile)

```bash
# Clone the repository
git clone <repository-url>
cd convo

# Complete setup in one command
make dev-setup

# Start the API server
make api

# Or try the interactive CLI
make cli
```

### Manual Setup

If you prefer manual setup or want more control:

#### 1. Installation

```bash
# Install dependencies
make install
# OR manually:
# poetry install  # or pip install -r requirements.txt
```

#### 2. Start Infrastructure

```bash
# Start MinIO object storage
make start-infra
# OR manually:
# docker-compose up -d
```

#### 3. Initialize Data

```bash
# Create tables, views, and generate sample data
make setup-data
# OR manually:
# python scripts/setup.py -a
```

This creates:
- **5000 conversations** with 1-8 interactions each (~15,000+ total entries)
- **Pre-built database views** for common analytics queries
- **Realistic retail scenarios**: Inventory, customer service, POS, safety, HR, seasonal
- **Partitioned storage**: Organized by date and hour for efficient queries

#### 4. Start the API Server

```bash
# Launch the FastAPI server
make api
# OR manually:
# python scripts/start_api.py

# API will be available at:
# - Interactive docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Health check: http://localhost:8000/health
```

## 🎯 Usage Examples

### REST API

```bash
# List all database views
curl http://localhost:8000/views

# Execute a pre-built view
curl "http://localhost:8000/views/interactions_per_day/execute?limit=10"

# AI-powered natural language query
curl "http://localhost:8000/query?q=Show me popular actions&debug=true"

# Browse interactive API documentation
open http://localhost:8000/docs
```

### Interactive CLI

```bash
# Configure AI provider (choose one)
export OPENAI_API_KEY="your-openai-key"
# OR
export GOOGLE_AI_API_KEY="your-google-key"

# Start interactive CLI
make cli
# OR manually:
# python cli/query_chat.py

# Example questions:
# - "How many conversations are there?"
# - "Show me interactions per day"
# - "What are the most popular actions?"
# - "Which sessions had multiple interactions?"
```

### Makefile Commands

The project includes a comprehensive Makefile for easy management:

```bash
# Get help with all available commands
make help

# Quick development setup
make dev-setup          # Complete setup: install, infra, data, views

# Infrastructure management
make start-infra        # Start MinIO with Docker Compose
make stop-infra         # Stop infrastructure
make restart-infra      # Clean restart with volume reset

# Data management
make setup              # Basic table setup
make setup-data         # Create sample data (5000+ conversations)
make clean-data         # Delete all data

# Services
make api                # Start FastAPI server
make cli                # Start interactive CLI

# Database views
make views-list         # List all available views
make views-create       # Create default views
make views-test         # Test views with sample data

# Testing and validation
make test               # Run all tests
make test-core          # Core functionality tests
make test-api           # API endpoint tests
make health             # System health check
make status             # Current system status

# Development tools
make format             # Format code (if black installed)
make lint               # Lint code (if flake8 installed)
make check-deps         # Check dependency availability

# Utilities
make clean              # Clean temporary files
make urls               # Show all service URLs
make info               # Project information
make demo               # Run complete demo
```

### Programmatic Access

```python
from convo.core.sql_agent import SQLAgent
from convo.core.view_manager import ViewManager

# AI-powered SQL generation
agent = SQLAgent()
results = agent.ask("Show me conversations by date")

# Database view management
vm = ViewManager()
views = vm.list_views()
vm.execute_view("interactions_per_day")
```

## 🗄️ Database Views

The platform includes pre-built analytical views that the AI agent automatically uses:

- **`interactions_per_day`**: Daily conversation counts and session statistics
- **`popular_actions`**: Most common action types with percentages
- **`active_sessions`**: Sessions with multiple interactions showing engagement
- **`recent_conversations`**: Last 7 days of conversation activity
- **`location_activity`**: Conversation activity grouped by store locations

### View Management

```bash
# List all views
python scripts/manage_views.py list

# Get view details
python scripts/manage_views.py show interactions_per_day

# Test a view
python scripts/manage_views.py test interactions_per_day --limit 5

# Create default views
python scripts/manage_views.py create-defaults
```

## 📊 Data Schema

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

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_core/      # Core functionality tests
pytest tests/test_api/       # API endpoint tests
pytest tests/integration/   # Integration tests

# Test project structure
python test_structure.py
```

## ⚙️ Configuration

The platform uses centralized configuration in `src/convo/config/settings.py`:

```python
# Environment variables (add to .env file)
OPENAI_API_KEY=your-openai-api-key
GOOGLE_AI_API_KEY=your-google-api-key
DEFAULT_AI_PROVIDER=openai

MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
BUCKET_NAME=convo

API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=false
```

## 🚀 Deployment

### Docker

```dockerfile
# Example Dockerfile (create as needed)
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "scripts/start_api.py"]
```

### Kubernetes

Basic deployment manifests can be created in `infrastructure/kubernetes/`:

```yaml
# Example deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: convo-analytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: convo-analytics
  template:
    spec:
      containers:
      - name: api
        image: convo-analytics:latest
        ports:
        - containerPort: 8000
```

## 🔧 Development

### Adding New Features

1. **Core Logic**: Add to `src/convo/core/`
2. **API Endpoints**: Add to `src/convo/api/routes/`
3. **Configuration**: Update `src/convo/config/settings.py`
4. **Tests**: Add to appropriate `tests/` subdirectory
5. **Documentation**: Update relevant docs

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 📚 API Documentation

The REST API provides comprehensive interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /health` - Service health check
- `GET /views` - List database views
- `GET /views/{name}/execute` - Execute a view
- `GET /query` - AI-powered natural language queries
- `POST /query` - AI queries with request body

## 🛠️ Management Commands

Using the Makefile (recommended):

```bash
# Setup and data management
make setup              # Basic setup
make setup-data         # Create sample data
make clean-data         # Delete all data

# API server
make api                # Start FastAPI server

# View management
make views-list         # List all views
make views-create       # Create default views
make views-test         # Test views with sample data

# Interactive CLI
make cli                # Natural language queries

# Infrastructure
make start-infra        # Start MinIO
make stop-infra         # Stop MinIO
make health             # Check system health
```

Or using direct script calls:

```bash
# Setup and data management
python scripts/setup.py           # Basic setup
python scripts/setup.py -a        # Create sample data
python scripts/setup.py -d        # Delete all data

# API server
python scripts/start_api.py       # Start FastAPI server

# View management
python scripts/manage_views.py list
python scripts/manage_views.py show view_name
python scripts/manage_views.py test view_name

# Interactive CLI
python cli/query_chat.py          # Natural language queries
```

## 🔍 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure you're in the project root and using the correct Python environment
python test_structure.py
```

**MinIO Connection Failed**
```bash
# Check MinIO status
docker-compose ps
curl http://localhost:9000/minio/health/live

# Restart if needed
docker-compose down
docker-compose up -d
```

**AI Query Errors**
```bash
# Verify API keys are configured
python -c "from convo.config.settings import validate_config; print(validate_config())"
```

**View Execution Errors**
```bash
# Test view management
python scripts/manage_views.py test interactions_per_day
```

## 📈 Performance

- **Partitioned Storage**: Queries filtering by date/hour are highly optimized
- **Columnar Format**: Parquet enables efficient analytical workloads
- **Pre-built Views**: Common queries cached for instant results
- **Connection Pooling**: Efficient database connection management
- **S3 Integration**: DuckDB's httpfs provides seamless cloud storage access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the project structure and add tests
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is for experimental and educational purposes.

---

For detailed project structure information, see [docs/project_structure.md](docs/project_structure.md)