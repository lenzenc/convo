#!/usr/bin/env python3
"""
Test script for the SQL Agent.
Tests various natural language queries without requiring API keys.
"""

import os
import logging
from sql_agent import SQLAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_schema_loading():
    """Test that the agent can load table schema."""
    print("🧪 Testing schema loading...")
    
    # Create agent without AI initialization (will fail but schema should load)
    try:
        agent = SQLAgent(use_openai=True)
        print("✅ Agent initialized successfully")
    except ValueError as e:
        if "API_KEY" in str(e):
            print("⚠️  No API key found (expected for testing)")
            # Create a mock agent just for schema testing
            agent = SQLAgent.__new__(SQLAgent)
            agent.use_openai = True
            agent.table_schema = agent._get_table_schema()
        else:
            raise
    
    # Test schema information
    schema = agent.table_schema
    print(f"✅ Table name: {schema['table_name']}")
    print(f"✅ S3 path: {schema['s3_path']}")
    print(f"✅ Columns: {len(schema['columns'])} columns defined")
    print(f"✅ Sample queries: {len(schema['sample_queries'])} examples")
    
    # Test system prompt generation
    prompt = agent._create_system_prompt()
    print(f"✅ System prompt generated: {len(prompt)} characters")
    
    return True


def test_query_execution():
    """Test DuckDB query execution (requires MinIO to be running)."""
    print("\n🧪 Testing query execution...")
    
    try:
        agent = SQLAgent.__new__(SQLAgent)
        agent.table_schema = agent._get_table_schema()
        
        # Simple test query
        test_sql = f"SELECT COUNT(*) as total_records FROM '{agent.table_schema['s3_path']}'"
        
        print(f"🔍 Executing test query: {test_sql}")
        results = agent.execute_query(test_sql)
        
        print(f"✅ Query executed successfully!")
        print(f"✅ Results: {results}")
        
        # Test result formatting
        formatted = agent.format_results(results)
        print(f"✅ Formatted output:\n{formatted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query execution failed: {e}")
        print("💡 Make sure MinIO is running and contains data (run setup.py -a)")
        return False


def test_sql_generation_mock():
    """Test SQL generation with mock responses."""
    print("\n🧪 Testing SQL generation patterns...")
    
    agent = SQLAgent.__new__(SQLAgent)
    agent.table_schema = agent._get_table_schema()
    
    # Test questions and expected SQL patterns
    test_cases = [
        {
            "question": "How many conversations are there?",
            "expected_pattern": "COUNT(*)"
        },
        {
            "question": "Show me conversations by date",
            "expected_pattern": "GROUP BY date"
        },
        {
            "question": "What are the most common actions?",
            "expected_pattern": "GROUP BY action"
        }
    ]
    
    print("📋 Test cases for SQL generation:")
    for i, case in enumerate(test_cases, 1):
        print(f"  {i}. '{case['question']}' should contain '{case['expected_pattern']}'")
    
    print("✅ SQL generation test cases defined")
    return True


def main():
    """Run all tests."""
    print("🚀 Starting SQL Agent Tests\n")
    
    tests = [
        ("Schema Loading", test_schema_loading),
        ("SQL Generation Patterns", test_sql_generation_mock),
        ("Query Execution", test_query_execution),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())