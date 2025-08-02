#!/usr/bin/env python3
"""
DuckDB View Management System for conversation analytics.
Manages creation, storage, and discovery of database views.
"""

import os
import json
import duckdb
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
from ..config.settings import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY,
    BUCKET_NAME, DUCKDB_CONNECTION, get_s3_config, get_table_s3_path
)

logger = logging.getLogger(__name__)


class ViewManager:
    """Manages DuckDB views for the conversation analytics system."""
    
    def __init__(self, views_config_path: str = None):
        """
        Initialize the ViewManager.
        
        Args:
            views_config_path: Path to the JSON file storing view definitions
        """
        if views_config_path is None:
            # Default to data/views_config.json relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            views_config_path = project_root / "data" / "views_config.json"
        
        self.views_config_path = Path(views_config_path)
        self.views = self._load_views_config()
        self.s3_path = get_table_s3_path()
    
    def _load_views_config(self) -> Dict[str, Dict]:
        """Load view definitions from JSON config file."""
        if not self.views_config_path.exists():
            # Create default config with empty views
            default_config = {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "views": {}
            }
            self._save_views_config(default_config)
            return default_config
        
        try:
            with open(self.views_config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading views config: {e}")
            return {"version": "1.0", "created": datetime.now().isoformat(), "views": {}}
    
    def _save_views_config(self, config: Dict) -> None:
        """Save view definitions to JSON config file."""
        try:
            config["last_updated"] = datetime.now().isoformat()
            with open(self.views_config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving views config: {e}")
            raise
    
    def _get_duckdb_connection(self) -> duckdb.DuckDBPyConnection:
        """Get configured DuckDB connection with S3 settings."""
        conn = duckdb.connect(DUCKDB_CONNECTION)
        
        # Install and load required extensions
        conn.execute("INSTALL httpfs;")
        conn.execute("LOAD httpfs;")
        
        # Configure S3 settings for MinIO
        s3_config = get_s3_config()
        for key, value in s3_config.items():
            conn.execute(f"SET {key} = '{value}';");
        
        return conn
    
    def create_view(self, view_name: str, description: str, sql_query: str, 
                   tags: List[str] = None, replace: bool = False) -> bool:
        """
        Create a new DuckDB view and store its definition.
        
        Args:
            view_name: Name of the view (must be valid SQL identifier)
            description: Human-readable description of what the view shows
            sql_query: The SQL query that defines the view
            tags: Optional list of tags for categorizing the view
            replace: Whether to replace existing view with same name
            
        Returns:
            True if view was created successfully, False otherwise
        """
        if not replace and view_name in self.views.get("views", {}):
            raise ValueError(f"View '{view_name}' already exists. Use replace=True to overwrite.")
        
        # Validate the SQL query by trying to execute it
        try:
            conn = self._get_duckdb_connection()
            
            # Test the query (limit to 1 row to avoid loading too much data)
            test_query = f"SELECT * FROM ({sql_query}) LIMIT 1"
            conn.execute(test_query)
            
            # Create the actual view
            create_view_sql = f"CREATE OR REPLACE VIEW {view_name} AS {sql_query}"
            conn.execute(create_view_sql)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error creating view '{view_name}': {e}")
            raise ValueError(f"Invalid SQL query for view '{view_name}': {e}")
        
        # Store view definition in config
        view_definition = {
            "name": view_name,
            "description": description,
            "sql_query": sql_query,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        
        self.views["views"][view_name] = view_definition
        self._save_views_config(self.views)
        
        logger.info(f"Successfully created view '{view_name}'")
        return True
    
    def get_view(self, view_name: str) -> Optional[Dict]:
        """Get view definition by name."""
        return self.views.get("views", {}).get(view_name)
    
    def list_views(self) -> List[Dict]:
        """List all available views with their metadata."""
        return list(self.views.get("views", {}).values())
    
    def delete_view(self, view_name: str) -> bool:
        """
        Delete a view from both DuckDB and the config.
        
        Args:
            view_name: Name of the view to delete
            
        Returns:
            True if view was deleted successfully, False if view didn't exist
        """
        if view_name not in self.views.get("views", {}):
            return False
        
        try:
            # Drop the view from DuckDB
            conn = self._get_duckdb_connection()
            conn.execute(f"DROP VIEW IF EXISTS {view_name}")
            conn.close()
            
            # Remove from config
            del self.views["views"][view_name]
            self._save_views_config(self.views)
            
            logger.info(f"Successfully deleted view '{view_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting view '{view_name}': {e}")
            raise
    
    def get_views_for_agent(self) -> List[Dict[str, str]]:
        """
        Get view information formatted for the SQL Agent.
        
        Returns:
            List of view dictionaries with name, description, and usage info
        """
        views_info = []
        for view_name, view_def in self.views.get("views", {}).items():
            views_info.append({
                "name": view_name,
                "description": view_def["description"],
                "tags": ", ".join(view_def.get("tags", [])),
                "usage": f"SELECT * FROM {view_name}",
                "created": view_def.get("created", ""),
                "sample_columns": self._get_view_columns(view_name)
            })
        return views_info
    
    def _get_view_columns(self, view_name: str) -> List[str]:
        """Get column names for a view."""
        try:
            conn = self._get_duckdb_connection()
            
            # First ensure the view exists in this connection
            view_def = self.get_view(view_name)
            if view_def:
                conn.execute(f"CREATE OR REPLACE VIEW {view_name} AS {view_def['sql_query']}")
            
            # Get column info
            result = conn.execute(f"DESCRIBE {view_name}").fetchall()
            columns = [row[0] for row in result]  # First column is column name
            
            conn.close()
            return columns
            
        except Exception as e:
            logger.warning(f"Could not get columns for view '{view_name}': {e}")
            return []
    
    def create_default_views(self) -> None:
        """Create a set of useful default views for conversation analytics."""
        default_views = [
            {
                "name": "interactions_per_day",
                "description": "Daily count of conversation interactions",
                "sql_query": f"""
                    SELECT 
                        date as "Date",
                        COUNT(*) as "Total Interactions",
                        COUNT(DISTINCT session_id) as "Unique Sessions",
                        AVG(interaction_id) as "Avg Interactions per Session"
                    FROM '{self.s3_path}'
                    GROUP BY date 
                    ORDER BY date DESC
                """,
                "tags": ["daily", "analytics", "summary"]
            },
            {
                "name": "popular_actions",
                "description": "Most common action types in conversations",
                "sql_query": f"""
                    SELECT 
                        action as "Action Type",
                        COUNT(*) as "Count",
                        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as "Percentage"
                    FROM '{self.s3_path}'
                    WHERE action IS NOT NULL
                    GROUP BY action 
                    ORDER BY COUNT(*) DESC
                """,
                "tags": ["actions", "popular", "percentage"]
            },
            {
                "name": "active_sessions",
                "description": "Sessions with multiple interactions (more engaging conversations)",
                "sql_query": f"""
                    SELECT 
                        session_id as "Session ID",
                        COUNT(*) as "Total Interactions",
                        MIN(question_created) as "First Question",
                        MAX(answer_created) as "Last Answer",
                        EXTRACT(EPOCH FROM (MAX(answer_created) - MIN(question_created))) / 60 as "Duration (minutes)"
                    FROM '{self.s3_path}'
                    GROUP BY session_id 
                    HAVING COUNT(*) > 1
                    ORDER BY COUNT(*) DESC
                """,
                "tags": ["sessions", "engagement", "duration"]
            },
            {
                "name": "recent_conversations",
                "description": "Conversations from the last 7 days",
                "sql_query": f"""
                    SELECT 
                        date as "Date",
                        session_id as "Session ID",
                        interaction_id as "Interaction",
                        LEFT(question, 50) || '...' as "Question Preview",
                        action as "Action Type",
                        user_id as "User ID",
                        location_id as "Store Location"
                    FROM '{self.s3_path}'
                    WHERE date >= CURRENT_DATE - INTERVAL 7 DAY
                    ORDER BY question_created DESC
                """,
                "tags": ["recent", "preview", "last-week"]
            },
            {
                "name": "location_activity",
                "description": "Conversation activity by store location",
                "sql_query": f"""
                    SELECT 
                        location_id as "Store Location",
                        region_id as "Region",
                        group_id as "Group",
                        district_id as "District",
                        COUNT(*) as "Total Conversations",
                        COUNT(DISTINCT session_id) as "Unique Sessions",
                        COUNT(DISTINCT user_id) as "Unique Users"
                    FROM '{self.s3_path}'
                    WHERE location_id IS NOT NULL
                    GROUP BY location_id, region_id, group_id, district_id
                    ORDER BY COUNT(*) DESC
                """,
                "tags": ["location", "geography", "stores"]
            }
        ]
        
        for view_def in default_views:
            try:
                self.create_view(
                    view_name=view_def["name"],
                    description=view_def["description"],
                    sql_query=view_def["sql_query"],
                    tags=view_def["tags"],
                    replace=True  # Allow overwriting existing default views
                )
                print(f"✅ Created view: {view_def['name']}")
            except Exception as e:
                print(f"❌ Failed to create view {view_def['name']}: {e}")


if __name__ == "__main__":
    # Example usage and testing
    manager = ViewManager()
    
    print("Creating default views...")
    manager.create_default_views()
    
    print("\nAvailable views:")
    for view in manager.list_views():
        print(f"- {view['name']}: {view['description']}")
        print(f"  Tags: {', '.join(view['tags'])}")
        print()