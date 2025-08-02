# Project Structure

This document describes the organized structure of the conversation analytics project.

## 📁 Directory Layout

```
convo/
├── README.md                    # Main project documentation
├── CLAUDE.md                    # Claude-specific instructions
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Lock file
├── docker-compose.yml          # Infrastructure setup
│
├── src/                        # Source code (main package)
│   └── convo/
│       ├── __init__.py
│       ├── core/               # Core business logic
│       │   ├── __init__.py
│       │   ├── view_manager.py # Database view management
│       │   └── sql_agent.py    # AI SQL generation
│       ├── api/                # REST API components
│       │   ├── __init__.py
│       │   ├── main.py         # FastAPI app
│       │   ├── models.py       # Pydantic models
│       │   └── routes/         # API route modules
│       │       ├── __init__.py
│       │       ├── health.py   # Health check endpoints
│       │       ├── views.py    # View-related endpoints
│       │       └── query.py    # AI query endpoints
│       └── config/             # Configuration management
│           ├── __init__.py
│           └── settings.py     # Environment variables, constants
│
├── scripts/                    # Utility and setup scripts
│   ├── setup.py               # Data setup and initialization
│   ├── manage_views.py        # View management CLI
│   └── start_api.py           # API server startup
│
├── cli/                       # Command-line interfaces
│   ├── __init__.py
│   └── query_chat.py          # Interactive query CLI
│
├── examples/                  # Usage examples and demos
│   ├── api_examples.py        # API usage examples
│   ├── demo_views.py          # View demonstration
│   └── query_example.py       # Basic query examples
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_core/
│   │   ├── __init__.py
│   │   ├── test_view_manager.py
│   │   └── test_sql_agent.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   └── test_endpoints.py
│   └── integration/
│       ├── __init__.py
│       └── test_setup.py
│
├── data/                      # Data files and configurations
│   └── views_config.json      # View definitions
│
├── docs/                      # Additional documentation
│   └── project_structure.md   # This file
│
└── infrastructure/            # Infrastructure and deployment
    ├── docker/
    └── kubernetes/
```

## 🎯 Key Principles

### 1. **Separation of Concerns**
- **Core business logic** (`src/convo/core/`) - Pure Python modules
- **API layer** (`src/convo/api/`) - FastAPI-specific code
- **CLI tools** (`scripts/` and `cli/`) - Command-line interfaces
- **Tests** (`tests/`) - Comprehensive test suite

### 2. **Proper Python Package Structure**
- `src/` layout prevents accidental imports during development
- `__init__.py` files make directories proper Python packages
- Clear module hierarchy with logical grouping

### 3. **Configuration Management**
- Centralized settings in `src/convo/config/`
- Environment-specific configurations
- Easy to modify without touching business logic

## 🚀 Usage Examples

### Import Core Components
```python
from convo.core.view_manager import ViewManager
from convo.core.sql_agent import SQLAgent
from convo.config.settings import BUCKET_NAME, get_s3_config
```

### Run Scripts
```bash
# Start API server
python scripts/start_api.py

# Manage views
python scripts/manage_views.py list

# Setup data
python scripts/setup.py -a

# Interactive CLI
python cli/query_chat.py
```

### Run Tests
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_core/
pytest tests/test_api/
pytest tests/integration/
```

## 📦 Benefits of This Structure

- ✅ **Professional Layout**: Standard Python project structure
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Testable**: Organized test suite with fixtures
- ✅ **Scalable**: Easy to add new features and modules
- ✅ **Configurable**: Centralized configuration management
- ✅ **Packageable**: Ready for distribution and deployment