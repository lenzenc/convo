#!/usr/bin/env python3
"""
Pydantic models for API request and response handling.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ViewInfo(BaseModel):
    """Information about a database view."""
    name: str
    description: str
    tags: List[str]
    created: str
    updated: str
    sample_columns: List[str]


class QueryRequest(BaseModel):
    """Request model for AI-powered queries."""
    question: str
    debug: bool = False


class QueryResponse(BaseModel):
    """Response model for query results."""
    question: str
    sql_query: Optional[str] = None
    execution_time_ms: float
    row_count: int
    data: List[Dict[str, Any]]
    error: Optional[str] = None


class ViewExecutionResponse(BaseModel):
    """Response model for view execution results."""
    view_name: str
    execution_time_ms: float
    row_count: int
    data: List[Dict[str, Any]]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    timestamp: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str
    components: Dict[str, bool]
    timestamp: str