#!/usr/bin/env python3
"""
Configuration management for the conversation analytics application.
Centralizes all environment variables and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MinIO/S3 Configuration
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'convo')

# Database Configuration
DUCKDB_CONNECTION = os.getenv('DUCKDB_CONNECTION', ':memory:')

# AI Configuration
DEFAULT_AI_PROVIDER = os.getenv('DEFAULT_AI_PROVIDER', 'openai')
DEFAULT_AI_MODEL = os.getenv('DEFAULT_AI_MODEL', 'gpt-4')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))

# Application Configuration
MAX_DISPLAY_ROWS = int(os.getenv('MAX_DISPLAY_ROWS', '10'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Data Generation Configuration (for setup.py)
NUM_CONVERSATIONS = int(os.getenv('NUM_CONVERSATIONS', '5000'))
FAILURE_RESPONSE_RATE = int(os.getenv('FAILURE_RESPONSE_RATE', '25'))
DATA_TIMESPAN_DAYS = int(os.getenv('DATA_TIMESPAN_DAYS', '90'))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1000'))

# View Configuration
DEFAULT_VIEWS_CONFIG_PATH = os.getenv('VIEWS_CONFIG_PATH', 'views_config.json')


def get_s3_config() -> dict:
    """Get S3 configuration dictionary for DuckDB."""
    endpoint = MINIO_ENDPOINT.replace('http://', '').replace('https://', '')
    return {
        's3_endpoint': endpoint,
        's3_access_key_id': MINIO_ACCESS_KEY,
        's3_secret_access_key': MINIO_SECRET_KEY,
        's3_use_ssl': 'true' if 'https' in MINIO_ENDPOINT else 'false',
        's3_url_style': 'path'
    }


def get_table_s3_path() -> str:
    """Get the S3 path for the main conversation table."""
    return f"s3://{BUCKET_NAME}/tables/conversation_entry/**/*.parquet"


def validate_config() -> dict:
    """Validate configuration and return status."""
    issues = []
    
    # Check AI API keys
    if not OPENAI_API_KEY and not GOOGLE_AI_API_KEY:
        issues.append("No AI API keys configured (OPENAI_API_KEY or GOOGLE_AI_API_KEY)")
    
    # Check required settings
    if not BUCKET_NAME:
        issues.append("BUCKET_NAME not configured")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "ai_provider": DEFAULT_AI_PROVIDER,
        "bucket": BUCKET_NAME,
        "minio_endpoint": MINIO_ENDPOINT
    }