#!/usr/bin/env python3
"""
Database view related endpoints.
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from ..models import ViewInfo, ViewExecutionResponse
from ...core.view_manager import ViewManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/views", tags=["Views"])

# Initialize view manager
try:
    view_manager = ViewManager()
    logger.info("View manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize view manager: {e}")
    view_manager = None


def serialize_data(data: List[dict]) -> List[dict]:
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


@router.get("", response_model=List[ViewInfo], summary="List all available views")
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


@router.get("/{view_name}", summary="Get view details")
async def get_view_details(view_name: str):
    """Get detailed information about a specific view."""
    if not view_manager:
        raise HTTPException(status_code=503, detail="View manager not available")
    
    view = view_manager.get_view(view_name)
    if not view:
        raise HTTPException(status_code=404, detail=f"View '{view_name}' not found")
    
    return view


@router.get("/{view_name}/execute", response_model=ViewExecutionResponse, summary="Execute a view")
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