#!/usr/bin/env python3
"""
Health check endpoints for the API.
"""

from datetime import datetime
from fastapi import APIRouter
from ..models import HealthResponse, DetailedHealthResponse

router = APIRouter(tags=["Health"])


@router.get("/", response_model=HealthResponse, summary="Health check")
async def root():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="Conversation Analytics API",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@router.get("/health", response_model=DetailedHealthResponse, summary="Detailed health check")
async def health_check():
    """Detailed health check with component status."""
    # Import here to avoid circular imports
    from ...core.view_manager import ViewManager
    from ...core.sql_agent import SQLAgent
    
    # Check component availability
    view_manager_available = True
    sql_agent_available = True
    
    try:
        ViewManager()
    except Exception:
        view_manager_available = False
    
    try:
        SQLAgent()
    except Exception:
        sql_agent_available = False
    
    components = {
        "view_manager": view_manager_available,
        "sql_agent": sql_agent_available,
    }
    
    all_healthy = all(components.values())
    
    return DetailedHealthResponse(
        status="healthy" if all_healthy else "degraded",
        components=components,
        timestamp=datetime.now().isoformat()
    )