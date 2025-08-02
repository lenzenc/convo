#!/usr/bin/env python3
"""
AI Agent for converting natural language to DuckDB SQL queries.
Uses Google AI SDK and OpenAI for natural language processing.
"""

import os
import re
import logging
import duckdb
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
from .view_manager import ViewManager

# Load environment variables
load_dotenv()

# Import configuration
from ..config.settings import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, BUCKET_NAME,
    DEFAULT_AI_PROVIDER, DEFAULT_AI_MODEL, DUCKDB_CONNECTION,
    MAX_DISPLAY_ROWS, LOG_LEVEL, DEBUG_MODE, OPENAI_API_KEY, GOOGLE_AI_API_KEY,
    get_s3_config, get_table_s3_path
)

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)


class SQLAgent:
    """AI Agent for natural language to SQL conversion and query execution."""
    
    def __init__(self, use_openai: bool = None):
        """
        Initialize the SQL Agent.
        
        Args:
            use_openai: If True, use OpenAI. If False, use Google AI. 
                       If None, use DEFAULT_AI_PROVIDER from environment.
        """
        if use_openai is None:
            self.use_openai = DEFAULT_AI_PROVIDER.lower() == 'openai'
        else:
            self.use_openai = use_openai
        self.table_schema = self._get_table_schema()
        self.view_manager = ViewManager()
        self.available_views = self.view_manager.get_views_for_agent()
        
        # Initialize AI clients
        if self.use_openai:
            self.openai_client = self._init_openai()
        else:
            self._init_google_ai()
    
    def _init_openai(self) -> OpenAI:
        """Initialize OpenAI client."""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return OpenAI(api_key=OPENAI_API_KEY)
    
    def _init_google_ai(self):
        """Initialize Google AI client."""
        if not GOOGLE_AI_API_KEY:
            raise ValueError("GOOGLE_AI_API_KEY environment variable not set")
        genai.configure(api_key=GOOGLE_AI_API_KEY)
        self.google_model = genai.GenerativeModel('gemini-pro')
    
    def _get_table_schema(self) -> Dict[str, Any]:
        """Get the schema information for the conversation_entry table."""
        return {
            "table_name": "conversation_entry",
            "s3_path": get_table_s3_path(),
            "columns": {
                "entry_id": "VARCHAR - Unique identifier (session_id + interaction_id)",
                "session_id": "VARCHAR - Session identifier for grouping conversations",
                "interaction_id": "INTEGER - Sequential number within a session (1, 2, 3...)",
                "date": "DATE - Date of the conversation",
                "hour": "INTEGER - Hour of day (0-23)",
                "question": "VARCHAR - The question asked by the user",
                "question_created": "TIMESTAMPTZ - Timestamp when question was asked",
                "answer": "VARCHAR - The AI response to the question",
                "answer_created": "TIMESTAMPTZ - Timestamp when answer was provided",
                "action": "VARCHAR - Action type (general, orders, msa_agents, inventory, customer_service, safety)",
                "user_id": "VARCHAR - ID of the user who asked the question",
                "location_id": "INTEGER - Store location ID (1001-1499)",
                "region_id": "INTEGER - Regional grouping (100-149)",
                "group_id": "INTEGER - Group identifier (10-24)",
                "district_id": "INTEGER - District identifier (1-14)",
                "user_roles": "VARCHAR[] - Array of user roles (team_member, team_lead, etc.)",
                "sources": "STRUCT(name VARCHAR, score FLOAT)[] - RAG sources with relevance scores"
            },
            "sample_queries": [
                "SELECT COUNT(*) FROM conversation_entry",
                "SELECT session_id, COUNT(*) as interactions FROM conversation_entry GROUP BY session_id",
                "SELECT date, COUNT(*) as daily_conversations FROM conversation_entry GROUP BY date ORDER BY date",
                "SELECT action, COUNT(*) as count FROM conversation_entry GROUP BY action ORDER BY count DESC"
            ]
        }
    
    def _format_views_for_prompt(self) -> str:
        """Format available views for inclusion in the system prompt."""
        if not self.available_views:
            return "No views are currently available."
        
        views_text = ""
        for view in self.available_views:
            views_text += f"""
VIEW: {view['name']}
Description: {view['description']}
Usage: {view['usage']}
Tags: {view['tags']}
Sample Columns: {', '.join(view['sample_columns']) if view['sample_columns'] else 'N/A'}
"""
        return views_text.strip()
    
    def _create_views_in_connection(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Create all available views in the given DuckDB connection."""
        try:
            for view_name, view_def in self.view_manager.views.get("views", {}).items():
                create_view_sql = f"CREATE OR REPLACE VIEW {view_name} AS {view_def['sql_query']}"
                conn.execute(create_view_sql)
                logger.debug(f"Created view '{view_name}' in connection")
        except Exception as e:
            logger.warning(f"Error creating views in connection: {e}")
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt with table schema information."""
        schema_info = self.table_schema
        
        # Get current date for relative date queries
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        
        prompt = f"""You are a DuckDB SQL expert. Your job is to convert natural language questions into valid DuckDB SQL queries.

TABLE SCHEMA:
Table: {schema_info['table_name']}
S3 Path: {schema_info['s3_path']}

COLUMNS:
"""
        
        for col, desc in schema_info['columns'].items():
            prompt += f"- {col}: {desc}\n"
        
        prompt += f"""
CURRENT DATE CONTEXT:
- Today's date: {today}
- Yesterday: {yesterday}
- Two days ago: {two_days_ago}

AVAILABLE VIEWS:
{self._format_views_for_prompt()}

IMPORTANT DUCKDB SYNTAX RULES:
1. **PREFER VIEWS WHEN AVAILABLE**: If a user's question matches the purpose of an available view, use the view instead of querying the raw S3 data directly
2. Query from the S3 path: '{schema_info['s3_path']}' only when no suitable view exists
3. Use proper DuckDB syntax for arrays and structs
4. For array columns like user_roles, use array syntax: user_roles[1] for first element
5. For struct arrays like sources, use: sources[1].name or sources[1].score
6. Date functions: Use EXTRACT(field FROM date) or date_part('field', date)
7. String matching: Use LIKE or ILIKE for case-insensitive
8. Always include proper GROUP BY clauses when using aggregations
9. NEVER use relative date terms like 'today', 'yesterday', etc. Always use explicit dates in YYYY-MM-DD format
10. For date comparisons, use proper DATE literals: DATE '2025-01-31'
11. NEVER use MySQL syntax like DATE_SUB(), DATE_ADD(), or INTERVAL - these don't work in DuckDB
12. For date arithmetic in DuckDB, use: CURRENT_DATE - INTERVAL 2 DAY or DATE '2025-01-31' - INTERVAL '2 days'
13. But PREFER using explicit date literals from the context provided above
14. **ALWAYS use human-readable column aliases instead of raw database column names**

COLUMN ALIASING REQUIREMENTS:
- Use meaningful, human-readable names for all columns in SELECT statements
- Transform technical column names into user-friendly labels
- Examples of good aliases:
  * session_id → "Session ID"
  * interaction_id → "Interaction"
  * question_created → "Question Time"
  * answer_created → "Answer Time"
  * user_id → "User ID"
  * location_id → "Store Location"
  * region_id → "Region"
  * group_id → "Group"
  * district_id → "District"
  * user_roles → "User Roles"
  * COUNT(*) → "Total Count"
  * COUNT(DISTINCT session_id) → "Unique Sessions"
  * AVG(interaction_id) → "Average Interactions"

FORBIDDEN SYNTAX (DO NOT USE):
- DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY) ❌
- DATE_ADD(date, INTERVAL 1 DAY) ❌
- CURDATE() ❌

CORRECT DUCKDB DATE SYNTAX:
- CURRENT_DATE ✅
- DATE '2025-01-31' ✅
- CURRENT_DATE - INTERVAL 2 DAY ✅
- date >= DATE '2025-01-24' AND date <= DATE '2025-01-31' ✅

DATE HANDLING EXAMPLES:
- "conversations from today" → WHERE date = DATE '{today}'
- "conversations from yesterday" → WHERE date = DATE '{yesterday}'
- "conversations from two days ago" → WHERE date = DATE '{two_days_ago}'
- "conversations from last week" → WHERE date >= DATE '{today - timedelta(days=7)}' AND date < DATE '{today}'

SAMPLE QUERIES:
{chr(10).join(schema_info['sample_queries'])}

RESPONSE FORMAT:
Return ONLY the SQL query, no explanations or markdown formatting. The query should be ready to execute directly in DuckDB.

EXAMPLES:
User: "How many conversations are there?"
Response: SELECT COUNT(*) as "Total Conversations" FROM '{schema_info['s3_path']}'

User: "Show me conversations by date" OR "Show me interactions per day"
Response: SELECT * FROM interactions_per_day

User: "What are the most common actions?" OR "Show me popular actions"
Response: SELECT * FROM popular_actions

User: "Show me active sessions" OR "Which sessions had multiple interactions?"
Response: SELECT * FROM active_sessions

User: "Show me recent conversations" OR "What happened in the last week?"
Response: SELECT * FROM recent_conversations

User: "Show me activity by location" OR "Which stores are most active?"
Response: SELECT * FROM location_activity

User: "Show me all conversations from two days ago"
Response: SELECT session_id as "Session ID", interaction_id as "Interaction", question as "Question", answer as "Answer", user_id as "User ID", location_id as "Store Location" FROM '{schema_info['s3_path']}' WHERE date = DATE '{two_days_ago}'

VIEW USAGE PRIORITY:
- If the user asks about daily interactions, conversation counts by date, or similar → use interactions_per_day view
- If the user asks about popular actions, action types, or action statistics → use popular_actions view  
- If the user asks about active sessions, engagement, or multi-interaction sessions → use active_sessions view
- If the user asks about recent data or last week's conversations → use recent_conversations view
- If the user asks about store locations, geography, or regional activity → use location_activity view
- Only query the raw S3 data directly when no existing view matches the user's request
"""
        return prompt
    
    def _generate_sql_openai(self, question: str) -> str:
        """Generate SQL using OpenAI."""
        try:
            response = self.openai_client.chat.completions.create(
                model=DEFAULT_AI_MODEL,
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": question}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _generate_sql_google(self, question: str) -> str:
        """Generate SQL using Google AI."""
        try:
            prompt = f"{self._create_system_prompt()}\n\nUser Question: {question}\nSQL Query:"
            response = self.google_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Google AI API error: {e}")
            raise
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL query from natural language question."""
        logger.info(f"Generating SQL for: {question}")
        
        if self.use_openai:
            sql = self._generate_sql_openai(question)
        else:
            sql = self._generate_sql_google(question)
        
        # Clean up the SQL (remove markdown formatting if present)
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```\s*', '', sql)
        sql = sql.strip()
        
        logger.info(f"Generated SQL: {sql}")
        return sql
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute the SQL query against DuckDB with S3 data."""
        logger.info(f"Executing query: {sql}")
        
        # Connect to DuckDB using configuration
        conn = duckdb.connect(DUCKDB_CONNECTION)
        
        try:
            # Install and load required extensions
            conn.execute("INSTALL httpfs;")
            conn.execute("LOAD httpfs;")
            
            # Configure S3 settings for MinIO using environment variables
            s3_config = get_s3_config()
            for key, value in s3_config.items():
                conn.execute(f"SET {key} = '{value}';");
            
            # Create all available views in this connection
            self._create_views_in_connection(conn)
            
            # Execute the query
            result = conn.execute(sql).fetchall()
            
            # Get column names
            columns = [desc[0] for desc in conn.description]
            
            # Convert to list of dictionaries
            result_dicts = []
            for row in result:
                result_dicts.append(dict(zip(columns, row)))
            
            logger.info(f"Query returned {len(result_dicts)} rows")
            return result_dicts
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            conn.close()
    
    def ask(self, question: str) -> List[Dict[str, Any]]:
        """
        Main method: Convert natural language to SQL and execute query.
        
        Args:
            question: Natural language question about the data
            
        Returns:
            List of dictionaries representing query results
        """
        try:
            # Generate SQL from natural language
            sql = self.generate_sql(question)
            
            # Execute the query
            results = self.execute_query(sql)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing question '{question}': {e}")
            raise
    
    def format_results(self, results: List[Dict[str, Any]], max_rows: int = None) -> str:
        """Format query results for console display."""
        if not results:
            return "No results found."
        
        # Use configured max rows if not specified
        if max_rows is None:
            max_rows = MAX_DISPLAY_ROWS
        
        # Limit results for display
        display_results = results[:max_rows]
        
        # Get column names
        columns = list(display_results[0].keys())
        
        # Calculate column widths
        widths = {}
        for col in columns:
            widths[col] = max(len(str(col)), max(len(str(row.get(col, ''))) for row in display_results))
        
        # Create header
        header = " | ".join(col.ljust(widths[col]) for col in columns)
        separator = "-" * len(header)
        
        # Create rows
        rows = []
        for row in display_results:
            row_str = " | ".join(str(row.get(col, '')).ljust(widths[col]) for col in columns)
            rows.append(row_str)
        
        # Combine all parts
        output = [header, separator] + rows
        
        if len(results) > max_rows:
            output.append(f"\n... showing {max_rows} of {len(results)} total rows")
        
        return "\n".join(output)