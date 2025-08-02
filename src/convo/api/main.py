#!/usr/bin/env python3
"""
FastAPI main application for conversation analytics.
Provides REST endpoints for querying views and running AI-powered SQL generation.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, views, query

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Conversation Analytics API",
    description="REST API for querying conversation data using views and AI-powered SQL generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost:3001",  # Alternative React port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(views.router)
app.include_router(query.router)

logger.info("FastAPI application initialized with all routes")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Conversation Analytics API on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)