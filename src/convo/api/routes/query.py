#!/usr/bin/env python3
"""
AI-powered query endpoints.
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..models import QueryRequest, QueryResponse
from ...core.sql_agent import SQLAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["AI Query"])

# Initialize SQL agent
try:
    sql_agent = SQLAgent()
    logger.info("SQL agent initialized successfully")
except Exception as e:
    logger.warning(f"SQL agent initialization failed (API keys may be missing): {e}")
    sql_agent = None


def serialize_data(data: list) -> list:
    """Convert data types that aren't JSON serializable."""
    serialized = []
    for row in data:
        serialized_row = {}
        for key, value in row.items():
            if isinstance(value, datetime):
                serialized_row[key] = value.isoformat()
            elif hasattr(value, '__dict__'):  # Custom objects
                serialized_row[key] = str(value)
            else:
                serialized_row[key] = value
        serialized.append(serialized_row)
    return serialized


@router.post("", response_model=QueryResponse, summary="AI-powered query")
async def ai_query(request: QueryRequest):
    """Execute a natural language query using AI to generate SQL."""
    if not sql_agent:
        raise HTTPException(status_code=503, detail="SQL agent not available (check API keys)")
    
    start_time = datetime.now()
    
    try:
        # Generate and execute the query
        results = sql_agent.ask(request.question)
        sql_query = None
        
        # If debug mode, generate SQL separately to show it
        if request.debug:
            sql_query = sql_agent.generate_sql(request.question)
        
        # Serialize the data
        serialized_data = serialize_data(results)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QueryResponse(
            question=request.question,
            sql_query=sql_query,
            execution_time_ms=execution_time,
            row_count=len(serialized_data),
            data=serialized_data
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Error processing AI query '{request.question}': {e}")
        
        return QueryResponse(
            question=request.question,
            execution_time_ms=execution_time,
            row_count=0,
            data=[],
            error=str(e)
        )


@router.get("", summary="AI-powered query (GET)")
async def ai_query_get(
    q: str = Query(..., description="Natural language question"),
    debug: bool = Query(False, description="Show generated SQL query"),
    limit: Optional[int] = Query(None, description="Maximum number of rows to return", ge=1, le=10000)
):
    """Execute a natural language query using AI to generate SQL (GET version)."""
    if not sql_agent:
        raise HTTPException(status_code=503, detail="SQL agent not available (check API keys)")
    
    start_time = datetime.now()
    
    try:
        # Generate and execute the query
        sql_query = sql_agent.generate_sql(q)
        
        # Add limit if specified
        if limit and "LIMIT" not in sql_query.upper():
            sql_query += f" LIMIT {limit}"
        
        results = sql_agent.execute_query(sql_query)
        
        # Serialize the data
        serialized_data = serialize_data(results)
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response_data = {
            "question": q,
            "execution_time_ms": execution_time,
            "row_count": len(serialized_data),
            "data": serialized_data
        }
        
        if debug:
            response_data["sql_query"] = sql_query
        
        return response_data
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Error processing AI query '{q}': {e}")
        
        return JSONResponse(
            status_code=500,
            content={
                "question": q,
                "execution_time_ms": execution_time,
                "row_count": 0,
                "data": [],
                "error": str(e)
            }
        )