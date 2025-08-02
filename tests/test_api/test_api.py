#!/usr/bin/env python3
"""
Test script for the FastAPI conversation analytics API.
Tests endpoints without requiring the full server to be running.
"""

import os
import sys
import asyncio
from api import app, view_manager
from fastapi.testclient import TestClient

def test_api_endpoints():
    """Test the API endpoints using FastAPI's test client."""
    print("🧪 Testing Conversation Analytics API\n")
    
    # Create test client
    client = TestClient(app)
    
    # Test 1: Health check
    print("1. Testing health check endpoint...")
    response = client.get("/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed: {data['status']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    
    # Test 2: Detailed health check
    print("\n2. Testing detailed health check...")
    response = client.get("/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Detailed health check: {data['status']}")
        print(f"   Components: {data['components']}")
    else:
        print(f"❌ Detailed health check failed: {response.status_code}")
    
    # Test 3: List views
    print("\n3. Testing views listing...")
    response = client.get("/views")
    if response.status_code == 200:
        views = response.json()
        print(f"✅ Found {len(views)} views:")
        for view in views:
            print(f"   - {view['name']}: {view['description']}")
    else:
        print(f"❌ Views listing failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 4: Get specific view details
    print("\n4. Testing view details...")
    response = client.get("/views/interactions_per_day")
    if response.status_code == 200:
        view = response.json()
        print(f"✅ View details for 'interactions_per_day':")
        print(f"   Description: {view['description']}")
        print(f"   Tags: {view['tags']}")
    else:
        print(f"❌ View details failed: {response.status_code}")
    
    # Test 5: Execute a view (this will fail without MinIO running, but we can test the endpoint)
    print("\n5. Testing view execution...")
    response = client.get("/views/interactions_per_day/execute?limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ View execution successful: {data['row_count']} rows")
        if data['data']:
            print(f"   Sample data keys: {list(data['data'][0].keys())}")
    else:
        data = response.json()
        if data.get('error'):
            print(f"⚠️  View execution failed (expected without MinIO): {data['error'][:100]}...")
        else:
            print(f"❌ View execution failed: {response.status_code}")
    
    # Test 6: AI Query endpoint (will fail without API keys, but we can test the endpoint)
    print("\n6. Testing AI query endpoint...")
    response = client.get("/query?q=How many conversations are there?&debug=true&limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AI query successful: {data['row_count']} rows")
        if data.get('sql_query'):
            print(f"   Generated SQL: {data['sql_query']}")
    else:
        print(f"⚠️  AI query failed (expected without API keys): {response.status_code}")
    
    # Test 7: Invalid view
    print("\n7. Testing invalid view...")
    response = client.get("/views/nonexistent_view")
    if response.status_code == 404:
        print("✅ Correctly returned 404 for nonexistent view")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
    
    print("\n🎉 API endpoint testing completed!")


def test_direct_view_execution():
    """Test view execution directly without HTTP."""
    print("\n🔧 Testing direct view execution...")
    
    if not view_manager:
        print("❌ View manager not available")
        return
    
    try:
        # Test that views are loaded
        views = view_manager.list_views()
        print(f"✅ View manager has {len(views)} views loaded")
        
        # Test getting view details
        view = view_manager.get_view("interactions_per_day")
        if view:
            print(f"✅ Retrieved view details for 'interactions_per_day'")
            print(f"   SQL Preview: {view['sql_query'][:100]}...")
        else:
            print("❌ Could not retrieve view details")
    
    except Exception as e:
        print(f"❌ Error in direct view testing: {e}")


if __name__ == "__main__":
    test_api_endpoints()
    test_direct_view_execution()