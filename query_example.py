#!/usr/bin/env python3
"""
Example script showing how to query tables stored in S3 with DuckDB.
"""

import duckdb
import logging

# Configuration
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
BUCKET_NAME = "convo"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def query_conversation_data():
    """Example of querying conversation data from S3."""
    logger.info("Connecting to DuckDB and querying S3 data...")
    
    # Connect to DuckDB in-memory
    conn = duckdb.connect(':memory:')
    
    try:
        # Install and load required extensions
        conn.execute("INSTALL httpfs;")
        conn.execute("LOAD httpfs;")
        
        # Configure S3 settings for MinIO
        conn.execute(f"""
            SET s3_endpoint = 'localhost:9000';
            SET s3_access_key_id = '{MINIO_ACCESS_KEY}';
            SET s3_secret_access_key = '{MINIO_SECRET_KEY}';
            SET s3_use_ssl = false;
            SET s3_url_style = 'path';
        """)
        
        # Query the table stored in S3
        # Note: This will work once data is inserted
        result = conn.execute(f"""
            SELECT COUNT(*) as total_conversations
            FROM 's3://{BUCKET_NAME}/tables/conversation_entry/**/*.parquet'
        """).fetchone()
        
        logger.info(f"Total conversations: {result[0]}")
        
        # Example: Insert sample data
        logger.info("Inserting sample data...")
        sample_data = """
            INSERT INTO temp_conversation_entry VALUES 
            ('session1_1', 'session1', 1, '2025-08-01', 14, 
             'What is the weather today?', '2025-08-01 14:30:00+00', 
             'I cannot access real-time weather data.', '2025-08-01 14:30:05+00',
             'general', 'user123', 1001, 101, 11, 1, 
             ['user'], [{'name': 'weather_api', 'score': 0.85}]);
        """
        
        # Create temp table with same structure
        conn.execute(f"""
            CREATE TEMP TABLE temp_conversation_entry (
                entry_id VARCHAR,
                session_id VARCHAR,
                interaction_id INTEGER,
                date DATE,
                hour INTEGER,
                question VARCHAR,
                question_created TIMESTAMPTZ,
                answer VARCHAR,
                answer_created TIMESTAMPTZ,
                action VARCHAR,
                user_id VARCHAR,
                location_id INTEGER,
                region_id INTEGER,
                group_id INTEGER,
                district_id INTEGER,
                user_roles VARCHAR[],
                sources STRUCT(name VARCHAR, score FLOAT)[]
            );
        """)
        
        conn.execute(sample_data)
        
        # Export sample data to S3
        conn.execute(f"""
            COPY temp_conversation_entry 
            TO 's3://{BUCKET_NAME}/tables/conversation_entry/' 
            (FORMAT PARQUET, PARTITION_BY (date, hour));
        """)
        
        logger.info("Sample data inserted into S3")
        
        # Query the data back
        result = conn.execute(f"""
            SELECT session_id, question, answer, date, hour
            FROM 's3://{BUCKET_NAME}/tables/conversation_entry/**/*.parquet'
            LIMIT 5
        """).fetchall()
        
        logger.info("Sample queries:")
        for row in result:
            logger.info(f"  Session: {row[0]}, Q: {row[1][:50]}...")
            
    finally:
        conn.close()


if __name__ == "__main__":
    query_conversation_data()