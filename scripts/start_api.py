#!/usr/bin/env python3
"""
Startup script for the Conversation Analytics API server.
"""

import sys
import os
import uvicorn
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting Conversation Analytics API Server")
    logger.info("📖 API Documentation available at: http://localhost:8000/docs")
    logger.info("📚 ReDoc Documentation available at: http://localhost:8000/redoc")
    logger.info("💡 Example queries:")
    logger.info("   GET /views - List all views")
    logger.info("   GET /views/interactions_per_day/execute - Execute a view")
    logger.info("   GET /query?q=Show me interactions per day - AI-powered query")
    
    uvicorn.run(
        "convo.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )