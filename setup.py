#!/usr/bin/env python3
"""
Setup script for conversation analytics project.
Creates MinIO S3 bucket and DuckDB tables with sample data.
"""

import boto3
import duckdb
from botocore.exceptions import ClientError
import logging
import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone
import json

# Configuration
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
BUCKET_NAME = "convo"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data for realistic retail conversations
RETAIL_QUESTIONS = [
    # Inventory & Stock
    "How do I check the current stock level for item SKU 12345?",
    "What's the procedure for restocking shelves in Electronics?",
    "How do I handle damaged merchandise on the sales floor?",
    "Where can I find the inventory count for back-to-school supplies?",
    "What's the protocol when an item shows in stock but I can't find it?",
    "How do I request a stock transfer from another store?",
    "What do I do with overstock items that don't fit on shelves?",
    "How do I update inventory after receiving a truck delivery?",
    
    # Customer Service
    "How do I process a return without a receipt?",
    "What's the store policy on price matching with competitors?",
    "How do I handle a customer complaint about a broken product?",
    "Can customers return items purchased online to our store?",
    "What's the procedure for issuing store credit?",
    "How do I help a customer find a specific product in the store?",
    "What should I do if a customer wants to speak to a manager?",
    "How do I process an exchange for a different size?",
    
    # Point of Sale / Register
    "How do I apply a discount code at the register?",
    "What's the procedure for processing a void transaction?",
    "How do I handle when the card reader isn't working?",
    "What do I do if the barcode won't scan?",
    "How do I process a layaway payment?",
    "What's the maximum amount for a cash transaction?",
    "How do I check if a coupon is valid?",
    "What do I do when the register drawer gets stuck?",
    
    # Safety & Security
    "What's the emergency procedure for a fire alarm?",
    "How do I report a safety hazard in the store?",
    "What should I do if I suspect shoplifting?",
    "Where are the first aid supplies located?",
    "What's the protocol for a medical emergency with a customer?",
    "How do I report a spill in an aisle?",
    "What do I do if the security cameras aren't working?",
    "Who do I contact for suspicious activity?",
    
    # Scheduling & HR
    "How do I request time off in the system?",
    "What's the dress code for seasonal workers?",
    "How do I swap shifts with another team member?",
    "What do I do if I'm going to be late for my shift?",
    "How do I access my work schedule online?",
    "What's the procedure for calling out sick?",
    "How do I update my emergency contact information?",
    "What are the break policies for an 8-hour shift?",
    
    # Seasonal & Promotions
    "What's the current promotion for back-to-school items?",
    "How do I set up holiday displays in my department?",
    "What items are on clearance this week?",
    "How do I apply seasonal pricing changes?",
    "What's the end date for the current sale?",
    "How do I handle pre-orders for holiday items?",
    "What's the markdown schedule for summer clothing?",
    "How do I activate promotional signage?",
]

RETAIL_ANSWERS = [
    # Inventory & Stock responses
    "You can check stock levels by scanning the item barcode in the MyDevice app or looking it up by SKU in the inventory system.",
    "For Electronics restocking, use the priority list in MyWork and focus on high-velocity items first. Check with your Team Lead for specific guidance.",
    "Damaged merchandise should be sorted into salvage bins and processed through the damaged goods system. Document the damage reason.",
    "Back-to-school inventory is tracked in seasonal reporting. Check the BTS dashboard in MyWork for current counts.",
    "If an item shows in stock but you can't locate it, check recent sales, the backroom, and create a research task in the system.",
    "Stock transfers require TL approval. Submit a request through Store to Store Transfer in MyWork with justification.",
    "Overstock should be placed in back stock locations or sent to clearance if it's seasonal merchandise past its selling period.",
    "After truck delivery, scan all items into the system and ensure accurate counts are reflected in inventory.",
    
    # Customer Service responses
    "Returns without receipts can be processed using the customer's ID for items under $20, or store credit for higher amounts per policy.",
    "We price match with major competitors for identical items. The item must be in stock at the competitor and available for immediate purchase.",
    "For broken product complaints, apologize, offer immediate replacement or refund, and escalate to Guest Services if needed.",
    "Yes, most online purchases can be returned in-store. Check the packing slip for return eligibility and process normally.",
    "Store credit is issued as a merchandise card and can be processed at Guest Services or any register.",
    "Use the Target app to help locate products, or call the department directly. Walk the guest to the location when possible.",
    "Acknowledge the request and call for a Team Lead or Guest Services Manager immediately. Stay with the guest.",
    "Exchanges for different sizes follow the same process as returns - just add the new item to the transaction.",
    
    # POS responses
    "Discount codes are applied by scanning the barcode or entering the code manually in the discount field before completing payment.",
    "Void transactions require supervisor approval. Press the void button and wait for a Team Lead to enter their credentials.",
    "If the card reader isn't working, try a different reader or ask the guest to use a different payment method. Call for tech support.",
    "For items that won't scan, enter the DPCI manually or use the MyDevice to look up the barcode number.",
    "Layaway payments are processed through the layaway system. Scan the layaway barcode first, then process the payment amount.",
    "Cash transactions over $200 require manager approval. Large cash payments may need additional verification.",
    "Check coupon validity by scanning it first. The system will indicate if it's expired or doesn't apply to current items.",
    "If the register drawer is stuck, don't force it. Call for maintenance and use a different register if available.",
    
    # Safety responses
    "During fire alarms, immediately assist guests to exit via nearest emergency exit and report to your designated meeting area.",
    "Report safety hazards immediately to your Team Lead and through the safety reporting system. Block the area if necessary.",
    "If you suspect shoplifting, don't approach the individual. Contact Assets Protection or call for security immediately.",
    "First aid supplies are located at Guest Services, the break room, and with each Team Lead. Call for medical assistance if needed.",
    "For medical emergencies, call 911 first, then notify management. Stay with the person and provide basic first aid if trained.",
    "Spills should be cleaned immediately or blocked off until housekeeping arrives. Use wet floor signs to warn guests.",
    "Report camera issues to Assets Protection immediately as this affects store security coverage.",
    "Contact your Team Lead or Assets Protection for any suspicious activity. Document what you observed.",
    
    # HR responses
    "Time off requests are submitted through myTime self-service. Submit at least 2 weeks in advance for approval.",
    "Seasonal workers follow the same dress code: red shirt, khaki pants/skirts, closed-toe shoes. Name tag required.",
    "Shift swaps must be approved by your Team Lead. Both team members need to agree and meet scheduling requirements.",
    "If you're running late, call the store immediately and speak to your Team Lead. Notify as early as possible.",
    "Access your schedule through myTime online or the myTime mobile app using your team member login.",
    "Call out sick by speaking directly to your Team Lead at least 2 hours before your shift starts.",
    "Update emergency contacts through myTime self-service or ask HR to help you make the changes.",
    "8-hour shifts include a 30-minute unpaid lunch and two 15-minute paid breaks. Check with your TL for timing.",
    
    # Seasonal responses
    "Current back-to-school promotions include 20% off school supplies and BOGO on notebooks. Check weekly ad for details.",
    "Holiday displays should follow the planogram provided. Contact your Team Lead for specific setup instructions and timeline.",
    "Check the weekly price change report for clearance items. Most clearance is marked with yellow or red signage.",
    "Seasonal pricing changes are applied automatically overnight. Verify pricing accuracy during your shift.",
    "Current sale ends Sunday night. New promotions start Monday morning with the weekly ad cycle.",
    "Pre-orders require a 25% deposit and can be processed at Guest Services. Provide the guest with pickup information.",
    "Summer clothing follows a progressive markdown schedule: 30%, 50%, 70% off based on sell-through rates.",
    "Promotional signage is activated Sunday night for Monday promotions. Check that all signs match current pricing.",
]

USER_ROLES = ["team_member", "team_lead", "guest_services", "assets_protection", "hr", "electronics", "grocery", "style"]
ACTIONS = ["general", "orders", "msa_agents", "inventory", "customer_service", "safety"]
LOCATIONS = list(range(1001, 1500))  # Store numbers
REGIONS = list(range(100, 150))
GROUPS = list(range(10, 25))
DISTRICTS = list(range(1, 15))

RAG_SOURCES = [
    {"name": "store_handbook", "score": 0.85},
    {"name": "inventory_system", "score": 0.92},
    {"name": "customer_service_guide", "score": 0.78},
    {"name": "safety_procedures", "score": 0.88},
    {"name": "pos_manual", "score": 0.90},
    {"name": "hr_policies", "score": 0.82},
    {"name": "seasonal_guide", "score": 0.75},
    {"name": "product_database", "score": 0.87}
]


def setup_minio_bucket():
    """Create S3 bucket in MinIO if it doesn't exist."""
    logger.info("Setting up MinIO S3 bucket...")
    
    # Create S3 client for MinIO
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1'  # MinIO default region
    )
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        logger.info(f"Bucket '{BUCKET_NAME}' already exists")
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            # Bucket doesn't exist, create it
            try:
                s3_client.create_bucket(Bucket=BUCKET_NAME)
                logger.info(f"Created bucket '{BUCKET_NAME}'")
            except ClientError as create_error:
                logger.error(f"Failed to create bucket: {create_error}")
                raise
        else:
            logger.error(f"Error checking bucket: {e}")
            raise


def delete_table_data():
    """Delete all data from the conversation_entry table in S3."""
    logger.info("Deleting existing table data from S3...")
    
    # Create S3 client for MinIO
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1'
    )
    
    try:
        # List and delete all objects in the tables directory
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix='tables/conversation_entry/'
        )
        
        if 'Contents' in response:
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            s3_client.delete_objects(
                Bucket=BUCKET_NAME,
                Delete={'Objects': objects_to_delete}
            )
            logger.info(f"Deleted {len(objects_to_delete)} objects from S3")
        else:
            logger.info("No existing data found to delete")
            
    except ClientError as e:
        logger.error(f"Error deleting table data: {e}")
        raise


def generate_conversation_data(num_conversations=5000):
    """Generate realistic conversation data for retail operations."""
    logger.info(f"Generating {num_conversations} conversations...")
    
    conversations = []
    
    # Generate date range for past 3 months
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=90)
    
    session_counter = 1
    
    for i in range(num_conversations):
        # Generate random session info
        session_id = f"session_{session_counter:06d}"
        
        # Random number of interactions per conversation (1-8)
        num_interactions = random.randint(1, 8)
        
        # Random date within the past 3 months
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Generate consistent attributes for this session
        location_id = random.choice(LOCATIONS)
        user_id = f"user_{random.randint(10000, 99999)}"
        region_id = random.choice(REGIONS)
        group_id = random.choice(GROUPS)
        district_id = random.choice(DISTRICTS)
        user_roles = [random.choice(USER_ROLES)]
        
        # Sometimes add additional roles
        if random.random() < 0.3:
            user_roles.append(random.choice(USER_ROLES))
        
        # Generate interactions for this conversation
        for interaction_id in range(1, num_interactions + 1):
            # Each interaction happens within a few minutes of the previous
            if interaction_id > 1:
                random_date += timedelta(minutes=random.randint(1, 5))
            
            # Select question and corresponding answer
            qa_index = random.randint(0, len(RETAIL_QUESTIONS) - 1)
            question = RETAIL_QUESTIONS[qa_index]
            answer = RETAIL_ANSWERS[qa_index]
            
            # Add some variation to questions
            if random.random() < 0.2:
                question = question.replace("How do I", "Can you help me")
            if random.random() < 0.1:
                question = question + " Thanks!"
            
            # Generate answer timestamp (1-30 seconds after question)
            question_created = random_date
            answer_created = question_created + timedelta(seconds=random.randint(1, 30))
            
            # Generate RAG sources (1-3 sources per answer)
            num_sources = random.randint(1, 3)
            sources = []
            selected_sources = random.sample(RAG_SOURCES, num_sources)
            for source in selected_sources:
                # Add some score variation
                score_variation = random.uniform(-0.1, 0.1)
                sources.append({
                    "name": source["name"],
                    "score": max(0.1, min(1.0, source["score"] + score_variation))
                })
            
            conversation = {
                "entry_id": f"{session_id}_{interaction_id}",
                "session_id": session_id,
                "interaction_id": interaction_id,
                "date": random_date.date(),
                "hour": random_date.hour,
                "question": question,
                "question_created": question_created,
                "answer": answer,
                "answer_created": answer_created,
                "action": random.choice(ACTIONS),
                "user_id": user_id,
                "location_id": location_id,
                "region_id": region_id,
                "group_id": group_id,
                "district_id": district_id,
                "user_roles": user_roles,
                "sources": sources
            }
            
            conversations.append(conversation)
        
        session_counter += 1
        
        if (i + 1) % 500 == 0:
            logger.info(f"Generated {i + 1} conversations...")
    
    logger.info(f"Generated {len(conversations)} total conversation entries")
    return conversations


def setup_duckdb_tables(with_sample_data=False):
    """Create DuckDB tables stored in S3."""
    logger.info("Setting up DuckDB tables in S3...")
    
    # Connect to DuckDB in-memory (no local database file)
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
        
        if with_sample_data:
            # Generate and insert realistic conversation data
            conversations = generate_conversation_data()
            logger.info("Inserting conversation data into DuckDB...")
            
            # Create table structure
            conn.execute("""
                CREATE TABLE conversation_entry (
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
            
            # Insert data in batches for better performance
            batch_size = 1000
            for i in range(0, len(conversations), batch_size):
                batch = conversations[i:i + batch_size]
                
                # Prepare batch insert
                values = []
                for conv in batch:
                    # Convert sources to proper struct format
                    sources_str = "[" + ", ".join([
                        f"{{'name': '{s['name']}', 'score': {s['score']}}}" 
                        for s in conv['sources']
                    ]) + "]"
                    
                    # Convert user_roles to array format
                    roles_str = "[" + ", ".join([f"'{role}'" for role in conv['user_roles']]) + "]"
                    
                    values.append(f"""(
                        '{conv['entry_id']}',
                        '{conv['session_id']}',
                        {conv['interaction_id']},
                        '{conv['date']}',
                        {conv['hour']},
                        '{conv['question'].replace("'", "''")}',
                        '{conv['question_created'].isoformat()}',
                        '{conv['answer'].replace("'", "''")}',
                        '{conv['answer_created'].isoformat()}',
                        '{conv['action']}',
                        '{conv['user_id']}',
                        {conv['location_id']},
                        {conv['region_id']},
                        {conv['group_id']},
                        {conv['district_id']},
                        {roles_str},
                        {sources_str}
                    )""")
                
                # Execute batch insert
                insert_sql = f"INSERT INTO conversation_entry VALUES {', '.join(values)}"
                conn.execute(insert_sql)
                
                logger.info(f"Inserted batch {i//batch_size + 1}/{(len(conversations)-1)//batch_size + 1}")
            
            logger.info(f"Successfully inserted {len(conversations)} conversation entries")
            
        else:
            # Create table with minimal sample data to establish structure
            logger.info("Creating table structure with minimal sample data...")
            
            create_table_sql = """
                CREATE TABLE conversation_entry AS 
                SELECT 
                    'sample_entry' as entry_id,
                    'sample_session' as session_id,
                    1 as interaction_id,
                    CAST('2025-01-01' AS DATE) as date,
                    0 as hour,
                    'Sample question to establish table structure' as question,
                    CAST('2025-01-01 00:00:00+00' AS TIMESTAMPTZ) as question_created,
                    'Sample answer to establish table structure' as answer,
                    CAST('2025-01-01 00:00:01+00' AS TIMESTAMPTZ) as answer_created,
                    'setup' as action,
                    'setup_user' as user_id,
                    0 as location_id,
                    0 as region_id,
                    0 as group_id,
                    0 as district_id,
                    ['setup'] as user_roles,
                    [{'name': 'setup', 'score': 1.0}] as sources;
            """
            conn.execute(create_table_sql)
        
        # Export the data to S3 to create the table structure
        logger.info("Exporting data to S3...")
        conn.execute(f"""
            COPY conversation_entry 
            TO 's3://{BUCKET_NAME}/tables/conversation_entry/' 
            (FORMAT PARQUET, PARTITION_BY (date, hour));
        """)
        
        logger.info(f"Created table structure in s3://{BUCKET_NAME}/tables/conversation_entry/")
        
        # Show table info
        result = conn.execute("DESCRIBE conversation_entry;").fetchall()
        logger.info("Table schema:")
        for row in result:
            logger.info(f"  {row[0]}: {row[1]}")
            
        # Verify the file was created in S3
        try:
            test_query = conn.execute(f"""
                SELECT COUNT(*) FROM 's3://{BUCKET_NAME}/tables/conversation_entry/**/*.parquet'
            """).fetchone()
            logger.info(f"Verification: Found {test_query[0]} record(s) in S3 table")
        except Exception as e:
            logger.warning(f"Could not verify S3 table creation: {e}")
            
    finally:
        conn.close()


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description='Setup conversation analytics project')
    parser.add_argument('-a', '--add-data', action='store_true', 
                       help='Delete existing data and create sample conversation data')
    
    args = parser.parse_args()
    
    logger.info("Starting conversation analytics setup...")
    
    try:
        setup_minio_bucket()
        
        if args.add_data:
            logger.info("Add data flag detected - will create sample data")
            delete_table_data()
            setup_duckdb_tables(with_sample_data=True)
        else:
            setup_duckdb_tables(with_sample_data=False)
            
        logger.info("Setup completed successfully!")
        
        if args.add_data:
            logger.info("\nSample data created!")
            logger.info("- Generated 5000 realistic retail conversations")
            logger.info("- Data spans the past 3 months")
            logger.info("- Conversations grouped by session_id")
            logger.info("- Includes realistic retail operational Q&A")
        
        logger.info("\nNext steps:")
        logger.info("1. Start services: docker-compose up -d")
        logger.info("2. Run this script: python setup.py")
        logger.info("3. For sample data: python setup.py -a")
        logger.info("4. MinIO console: http://localhost:9001 (minioadmin/minioadmin123)")
        logger.info("5. Tables are stored in S3: s3://convo/tables/")
        logger.info("6. Query tables with DuckDB by reading from S3 paths")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise


if __name__ == "__main__":
    main()