#!/usr/bin/env python3
"""
FastAPI web service for conversation analytics.
Provides REST endpoints for querying views and running AI-powered SQL generation.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from view_manager import ViewManager
from sql_agent import SQLAgent

# Load environment variables
load_dotenv()

# Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Conversation Analytics API",
    description="REST API for querying conversation data using views and AI-powered SQL generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize components
try:
    view_manager = ViewManager()
    logger.info("View manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize view manager: {e}")
    view_manager = None

try:
    sql_agent = SQLAgent()
    logger.info("SQL agent initialized successfully")
except Exception as e:
    logger.warning(f"SQL agent initialization failed (API keys may be missing): {e}")
    sql_agent = None


# Pydantic models
class ViewInfo(BaseModel):
    name: str
    description: str
    tags: List[str]
    created: str
    updated: str
    sample_columns: List[str]


class QueryRequest(BaseModel):
    question: str
    debug: bool = False


class QueryResponse(BaseModel):
    question: str
    sql_query: Optional[str] = None
    execution_time_ms: float
    row_count: int
    data: List[Dict[str, Any]]
    error: Optional[str] = None


class ViewExecutionResponse(BaseModel):
    view_name: str
    execution_time_ms: float
    row_count: int
    data: List[Dict[str, Any]]
    error: Optional[str] = None


# Helper functions
def serialize_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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


# API Routes

@app.get("/", summary="Health check", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Conversation Analytics API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", summary="Detailed health check", tags=["Health"])
async def health_check():
    """Detailed health check with component status."""
    components = {
        "view_manager": view_manager is not None,
        "sql_agent": sql_agent is not None,
    }
    
    all_healthy = all(components.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "components": components,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/views", response_model=List[ViewInfo], summary="List all available views", tags=["Views"])
async def list_views():
    """Get a list of all available database views."""
    if not view_manager:
        raise HTTPException(status_code=503, detail="View manager not available")
    
    try:
        views_data = view_manager.get_views_for_agent()
        views = []
        
        for view_data in views_data:
            view_info = ViewInfo(
                name=view_data["name"],
                description=view_data["description"],
                tags=view_data["tags"].split(", ") if view_data["tags"] else [],
                created=view_data.get("created", ""),
                updated=view_data.get("created", ""),  # Using created as fallback
                sample_columns=view_data["sample_columns"]
            )
            views.append(view_info)
        
        return views
        
    except Exception as e:
        logger.error(f"Error listing views: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list views: {str(e)}")


@app.get("/views/{view_name}", summary="Get view details", tags=["Views"])
async def get_view_details(view_name: str):
    """Get detailed information about a specific view."""
    if not view_manager:
        raise HTTPException(status_code=503, detail="View manager not available")
    
    view = view_manager.get_view(view_name)
    if not view:
        raise HTTPException(status_code=404, detail=f"View '{view_name}' not found")
    
    return view


@app.get("/views/{view_name}/execute", response_model=ViewExecutionResponse, summary="Execute a view", tags=["Views"])
async def execute_view(
    view_name: str,
    limit: Optional[int] = Query(None, description="Maximum number of rows to return", ge=1, le=10000)
):
    """Execute a database view and return the results."""
    if not view_manager:
        raise HTTPException(status_code=503, detail="View manager not available")
    
    # Check if view exists
    view = view_manager.get_view(view_name)
    if not view:
        raise HTTPException(status_code=404, detail=f"View '{view_name}' not found")
    
    start_time = datetime.now()
    
    try:
        # Build the query
        query = f"SELECT * FROM {view_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        # Execute using the view manager's connection
        conn = view_manager._get_duckdb_connection()
        
        # Create the view in this connection
        create_view_sql = f"CREATE OR REPLACE VIEW {view_name} AS {view['sql_query']}"
        conn.execute(create_view_sql)
        
        # Execute the query
        result = conn.execute(query).fetchall()
        columns = [desc[0] for desc in conn.description]
        
        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in result]
        
        # Serialize the data
        serialized_data = serialize_data(data)
        
        conn.close()
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ViewExecutionResponse(
            view_name=view_name,
            execution_time_ms=execution_time,
            row_count=len(serialized_data),
            data=serialized_data
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Error executing view '{view_name}': {e}")
        
        return ViewExecutionResponse(
            view_name=view_name,
            execution_time_ms=execution_time,
            row_count=0,
            data=[],
            error=str(e)
        )


@app.post("/query", response_model=QueryResponse, summary="AI-powered query", tags=["AI Query"])
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


@app.get("/query", summary="AI-powered query (GET)", tags=["AI Query"])
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


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Conversation Analytics API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)