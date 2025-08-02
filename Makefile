# Conversation Analytics Platform Makefile
# Provides easy commands for running scripts and managing the project

.PHONY: help install clean start-infra stop-infra setup setup-data api cli ui test lint format check-deps health status views examples clean-data

# Default target
help: ## Show this help message
	@echo "🚀 Conversation Analytics Platform"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start: make install && make start-infra && make setup-data && make api"
	@echo "Full stack: Add 'make ui' in another terminal for the React dashboard"

# Installation and setup
install: ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	@if command -v poetry >/dev/null 2>&1; then \
		poetry install; \
	else \
		pip install -r requirements.txt; \
	fi
	@echo "✅ Dependencies installed"

clean: ## Clean up temporary files and caches
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -f api.log api.pid
	@echo "✅ Cleanup complete"

# Infrastructure management
start-infra: ## Start MinIO infrastructure with Docker Compose
	@echo "🐳 Starting infrastructure..."
	@docker compose up -d
	@echo "⏳ Waiting for MinIO to be ready..."
	@sleep 5
	@echo "✅ Infrastructure started"
	@echo "💡 MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)"

stop-infra: ## Stop MinIO infrastructure
	@echo "🛑 Stopping infrastructure..."
	@docker compose down
	@echo "✅ Infrastructure stopped"

restart-infra: ## Restart infrastructure (with volume cleanup)
	@echo "🔄 Restarting infrastructure..."
	@docker compose down -v
	@docker compose up -d
	@sleep 5
	@echo "✅ Infrastructure restarted with clean volumes"

# Data setup and management
setup: ## Basic setup (table structure only)
	@echo "⚙️ Running basic setup..."
	@python scripts/setup.py
	@echo "✅ Basic setup complete"

setup-data: ## Create sample data (recommended for development)
	@echo "📊 Creating sample data..."
	@python scripts/setup.py -a
	@echo "✅ Sample data created (5000+ conversations)"

clean-data: ## Delete all data from S3
	@echo "🗑️ Deleting all data..."
	@python scripts/setup.py -d
	@echo "✅ All data deleted"

# API and services
api: ## Start the FastAPI server
	@echo "🌐 Starting API server..."
	@echo "📖 API docs will be available at: http://localhost:8000/docs"
	@echo "💡 Press Ctrl+C to stop the server"
	@echo ""
	@python scripts/start_api.py || true

api-background: ## Start API server in background
	@echo "🌐 Starting API server in background..."
	@nohup python scripts/start_api.py > api.log 2>&1 & echo $$! > api.pid
	@sleep 2
	@echo "✅ API server started (PID: $$(cat api.pid))"
	@echo "📖 API docs: http://localhost:8000/docs"
	@echo "📋 Logs: tail -f api.log"
	@echo "🛑 Stop with: make api-stop"

api-stop: ## Stop background API server
	@if [ -f api.pid ]; then \
		PID=$$(cat api.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			kill $$PID; \
			echo "🛑 API server stopped (PID: $$PID)"; \
		else \
			echo "⚠️  API server not running"; \
		fi; \
		rm -f api.pid; \
	else \
		echo "⚠️  No API server PID file found"; \
	fi

# CLI tools
cli: ## Start interactive CLI for natural language queries
	@echo "💬 Starting interactive CLI..."
	@python cli/query_chat.py

# UI Development
ui: ## Start the React UI development server
	@echo "🎨 Starting React UI development server..."
	@echo "🌐 UI will be available at: http://localhost:3000"
	@echo "💡 Press Ctrl+C to stop the server"
	@echo ""
	@cd ui && npm start

# View management
views-list: ## List all database views
	@echo "📋 Available database views:"
	@python scripts/manage_views.py list

views-create: ## Create default database views
	@echo "🔨 Creating default views..."
	@python scripts/manage_views.py create-defaults
	@echo "✅ Default views created"

views-test: ## Test all views (show sample data)
	@echo "🧪 Testing database views..."
	@python scripts/manage_views.py test interactions_per_day --limit 3
	@python scripts/manage_views.py test popular_actions --limit 3
	@python scripts/manage_views.py test active_sessions --limit 3

# Testing
test: ## Run all tests
	@echo "🧪 Running tests..."
	@echo "📋 Structure validation:"
	@python -c "import sys; sys.path.insert(0, 'src'); from convo.core.view_manager import ViewManager; from convo.core.sql_agent import SQLAgent; from convo.config.settings import validate_config; vm=ViewManager(); print(f'✅ {len(vm.list_views())} views loaded'); print(f'✅ Config valid: {validate_config()[\"valid\"]}')"
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v --tb=short; \
	else \
		echo "⚠️  pytest not installed, running basic tests only"; \
		python tests/test_core/test_agent.py; \
		python tests/test_api/test_api.py; \
	fi
	@echo "✅ Tests complete"

test-core: ## Run core functionality tests
	@echo "🧪 Running core tests..."
	@python tests/test_core/test_agent.py
	@python tests/test_core/test_views.py

test-api: ## Run API tests
	@echo "🧪 Running API tests..."
	@python tests/test_api/test_api.py

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	@python tests/integration/test_setup_views.py

# Examples and demos
examples: ## Run example scripts
	@echo "📝 Running examples..."
	@echo "1. Basic query example:"
	@python examples/query_example.py
	@echo ""
	@echo "2. View demonstration:"
	@python examples/demo_views.py
	@echo ""
	@echo "3. API examples (requires API to be running):"
	@echo "   Start API in another terminal: make api"
	@echo "   Then run: python examples/api_examples.py"

# Health and status checks
health: ## Check system health and configuration
	@echo "🏥 System Health Check"
	@echo "====================="
	@echo "📦 Python environment:"
	@python --version
	@echo ""
	@echo "🐳 Docker services:"
	@docker compose ps
	@echo ""
	@echo "⚙️ Configuration validation:"
	@python -c "import sys; sys.path.insert(0, 'src'); from convo.config.settings import validate_config; result = validate_config(); print(f'✅ Valid: {result[\"valid\"]}'); [print(f'⚠️  {issue}') for issue in result['issues']]"
	@echo ""
	@echo "🗄️ Database views:"
	@python -c "import sys; sys.path.insert(0, 'src'); from convo.core.view_manager import ViewManager; vm = ViewManager(); views = vm.list_views(); print(f'✅ {len(views)} views available')"

status: ## Show current system status
	@echo "📊 System Status"
	@echo "==============="
	@echo "🐳 Infrastructure:"
	@if docker compose ps | grep -q "Up"; then \
		echo "  ✅ MinIO running"; \
	else \
		echo "  ❌ MinIO not running (run 'make start-infra')"; \
	fi
	@echo ""
	@echo "🌐 API endpoint test:"
	@if curl -s http://localhost:8000/health >/dev/null 2>&1; then \
		echo "  ✅ API responding at http://localhost:8000"; \
	else \
		echo "  ❌ API not responding (run 'make api')"; \
	fi

# Development tools
format: ## Format code with black (if available)
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black src/ tests/ --line-length 100; \
		echo "✅ Code formatted"; \
	else \
		echo "⚠️  black not installed, skipping formatting"; \
	fi

lint: ## Lint code with flake8 (if available)
	@echo "🔍 Linting code..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503; \
		echo "✅ Linting complete"; \
	else \
		echo "⚠️  flake8 not installed, skipping linting"; \
	fi

check-deps: ## Check if all dependencies are available
	@echo "📋 Dependency Check"
	@echo "=================="
	@python -c "import sys; print(f'Python: {sys.version}')"
	@echo ""
	@echo "Core dependencies:"
	@python -c "import duckdb; print('✅ duckdb')" || echo "❌ duckdb"
	@python -c "import fastapi; print('✅ fastapi')" || echo "❌ fastapi"
	@python -c "import uvicorn; print('✅ uvicorn')" || echo "❌ uvicorn"
	@python -c "import boto3; print('✅ boto3')" || echo "❌ boto3"
	@echo ""
	@echo "AI dependencies:"
	@python -c "import openai; print('✅ openai')" || echo "❌ openai"
	@python -c "import google.generativeai; print('✅ google-generativeai')" || echo "❌ google-generativeai"
	@echo ""
	@echo "CLI dependencies:"
	@python -c "import rich; print('✅ rich')" || echo "❌ rich"

# Complete workflows
dev-setup: ## Complete development setup
	@echo "🚀 Complete Development Setup"
	@echo "============================"
	@$(MAKE) install
	@$(MAKE) start-infra
	@$(MAKE) setup-data
	@$(MAKE) views-create
	@$(MAKE) health
	@echo ""
	@echo "🎉 Development environment ready!"
	@echo "💡 Next steps:"
	@echo "   - Start API: make api"
	@echo "   - Start UI (new terminal): make ui"
	@echo "   - Try CLI: make cli"
	@echo "   - Run tests: make test"
	@echo "   - View examples: make examples"

quick-start: ## Quick start for new users
	@echo "⚡ Quick Start Guide"
	@echo "==================="
	@echo "This will set up everything you need..."
	@$(MAKE) dev-setup

demo: ## Run a complete demo
	@echo "🎬 Running Demo"
	@echo "==============="
	@$(MAKE) health
	@echo ""
	@echo "📊 Sample view data:"
	@$(MAKE) views-test
	@echo ""
	@echo "📝 Running examples:"
	@$(MAKE) examples
	@echo ""
	@echo "🎉 Demo complete!"
	@echo "💡 Try 'make api' to start the web service"
	@echo "💡 Try 'make ui' to start the React dashboard"

# Docker shortcuts
docker-logs: ## Show Docker container logs
	@echo "📋 Container logs:"
	@docker compose logs

docker-stats: ## Show Docker container stats
	@echo "📊 Container stats:"
	@docker stats --no-stream

# Utility targets
urls: ## Show all relevant URLs
	@echo "🔗 Service URLs"
	@echo "==============="
	@echo "React Dashboard:   http://localhost:3000"
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "API ReDoc:         http://localhost:8000/redoc"
	@echo "API Health:        http://localhost:8000/health"
	@echo "MinIO Console:     http://localhost:9001"
	@echo "MinIO API:         http://localhost:9000"

env-example: ## Create example environment file
	@echo "📝 Creating .env.example..."
	@echo "# AI Configuration" > .env.example
	@echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env.example
	@echo "GOOGLE_AI_API_KEY=your-google-ai-api-key-here" >> .env.example
	@echo "DEFAULT_AI_PROVIDER=openai" >> .env.example
	@echo "DEFAULT_AI_MODEL=gpt-4" >> .env.example
	@echo "" >> .env.example
	@echo "# MinIO Configuration" >> .env.example
	@echo "MINIO_ENDPOINT=http://localhost:9000" >> .env.example
	@echo "MINIO_ACCESS_KEY=minioadmin" >> .env.example
	@echo "MINIO_SECRET_KEY=minioadmin123" >> .env.example
	@echo "BUCKET_NAME=convo" >> .env.example
	@echo "" >> .env.example
	@echo "# API Configuration" >> .env.example
	@echo "API_HOST=0.0.0.0" >> .env.example
	@echo "API_PORT=8000" >> .env.example
	@echo "" >> .env.example
	@echo "# Application Settings" >> .env.example
	@echo "DEBUG_MODE=false" >> .env.example
	@echo "LOG_LEVEL=INFO" >> .env.example
	@echo "MAX_DISPLAY_ROWS=10" >> .env.example
	@echo "" >> .env.example
	@echo "# Data Generation Settings" >> .env.example
	@echo "NUM_CONVERSATIONS=5000" >> .env.example
	@echo "FAILURE_RESPONSE_RATE=25" >> .env.example
	@echo "DATA_TIMESPAN_DAYS=90" >> .env.example
	@echo "BATCH_SIZE=1000" >> .env.example
	@echo "✅ Created .env.example"
	@echo "💡 Copy to .env and update with your settings"

# Project info
info: ## Show project information
	@echo "ℹ️  Project Information"
	@echo "======================"
	@echo "Name: Conversation Analytics Platform"
	@echo "Structure: Professional Python package"
	@echo ""
	@echo "📁 Key directories:"
	@echo "  src/convo/core/     - Core business logic"
	@echo "  src/convo/api/      - REST API components"
	@echo "  src/convo/config/   - Configuration"
	@echo "  scripts/            - Utility scripts"
	@echo "  cli/                - Command-line tools"
	@echo "  tests/              - Test suite"
	@echo "  examples/           - Usage examples"
	@echo ""
	@echo "🛠️  Available commands: make help"