#!/usr/bin/env python3
"""
Example usage of the Conversation Analytics REST API.
Demonstrates various API endpoints and response handling.
"""

import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def pretty_print_json(data: Dict[str, Any], title: str = "Response"):
    """Pretty print JSON data."""
    print(f"\n📊 {title}")
    print("=" * (len(title) + 4))
    print(json.dumps(data, indent=2, default=str))


def test_health_endpoints():
    """Test health check endpoints."""
    print("🔍 Testing Health Endpoints")
    
    # Basic health check
    response = requests.get(f"{API_BASE_URL}/")
    if response.status_code == 200:
        pretty_print_json(response.json(), "Basic Health Check")
    
    # Detailed health check
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        pretty_print_json(response.json(), "Detailed Health Check")


def test_view_endpoints():
    """Test view-related endpoints."""
    print("\n🔍 Testing View Endpoints")
    
    # List all views
    response = requests.get(f"{API_BASE_URL}/views")
    if response.status_code == 200:
        views = response.json()
        print(f"\n📋 Found {len(views)} views:")
        for view in views:
            print(f"  - {view['name']}: {view['description']}")
    
    # Get specific view details
    response = requests.get(f"{API_BASE_URL}/views/interactions_per_day")
    if response.status_code == 200:
        pretty_print_json(response.json(), "View Details: interactions_per_day")
    
    # Execute a view
    response = requests.get(f"{API_BASE_URL}/views/interactions_per_day/execute?limit=3")
    if response.status_code == 200:
        data = response.json()
        print(f"\n📈 View Execution Results:")
        print(f"  - View: {data['view_name']}")
        print(f"  - Execution Time: {data['execution_time_ms']:.2f}ms")
        print(f"  - Row Count: {data['row_count']}")
        if data['data']:
            print(f"  - Sample Row: {data['data'][0]}")
    
    # Test different views
    view_tests = [
        ("popular_actions", "Top 3 popular actions"),
        ("active_sessions", "Top 3 active sessions"),
        ("recent_conversations", "Recent conversations (last 5)"),
        ("location_activity", "Top 3 locations by activity")
    ]
    
    for view_name, description in view_tests:
        print(f"\n🔍 Testing {description}")
        response = requests.get(f"{API_BASE_URL}/views/{view_name}/execute?limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ {data['row_count']} rows in {data['execution_time_ms']:.2f}ms")
            if data.get('error'):
                print(f"  ⚠️  Error: {data['error']}")
        else:
            print(f"  ❌ Failed: {response.status_code}")


def test_ai_query_endpoints():
    """Test AI-powered query endpoints."""
    print("\n🔍 Testing AI Query Endpoints")
    
    # Test GET endpoint with various queries
    test_queries = [
        "Show me interactions per day",
        "What are the most popular actions?",
        "Which sessions are most active?",
        "How many conversations are there?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        response = requests.get(f"{API_BASE_URL}/query", params={
            "q": query,
            "debug": True,
            "limit": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ {data['row_count']} rows in {data['execution_time_ms']:.2f}ms")
            if data.get('sql_query'):
                print(f"  🔍 SQL: {data['sql_query']}")
            if data.get('error'):
                print(f"  ⚠️  Error: {data['error']}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    
    # Test POST endpoint
    print(f"\n🔍 Testing POST query endpoint")
    response = requests.post(f"{API_BASE_URL}/query", json={
        "question": "Show me the most popular actions with percentages",
        "debug": True
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ POST query successful: {data['row_count']} rows")
        if data.get('sql_query'):
            print(f"  🔍 Generated SQL: {data['sql_query']}")


def test_error_handling():
    """Test API error handling."""
    print("\n🔍 Testing Error Handling")
    
    # Test nonexistent view
    response = requests.get(f"{API_BASE_URL}/views/nonexistent_view")
    if response.status_code == 404:
        print("  ✅ Correctly returns 404 for nonexistent view")
    
    # Test invalid view execution
    response = requests.get(f"{API_BASE_URL}/views/nonexistent_view/execute")
    if response.status_code == 404:
        print("  ✅ Correctly returns 404 for nonexistent view execution")
    
    # Test invalid limit parameter
    response = requests.get(f"{API_BASE_URL}/views/interactions_per_day/execute?limit=invalid")
    if response.status_code == 422:
        print("  ✅ Correctly validates query parameters")


def main():
    """Run all API tests."""
    print("🚀 Conversation Analytics API Examples")
    print("=" * 45)
    
    try:
        # Check if API is running
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ API is not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Make sure it's running:")
        print("   python start_api.py")
        return
    
    print("✅ Connected to API successfully\n")
    
    # Run tests
    test_health_endpoints()
    test_view_endpoints()
    test_ai_query_endpoints()
    test_error_handling()
    
    print("\n🎉 API examples completed!")
    print("\n💡 Try the interactive API docs at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()