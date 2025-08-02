#!/usr/bin/env python3
"""
Test script specifically for the view functionality.
"""

import os
from sql_agent import SQLAgent
from view_manager import ViewManager

def test_view_integration():
    """Test that views are properly integrated with the SQL agent."""
    print("🧪 Testing view integration...")
    
    # Test view manager
    vm = ViewManager()
    views = vm.list_views()
    print(f"✅ Found {len(views)} views")
    
    for view in views:
        print(f"  - {view['name']}: {view['description']}")
    
    # Test that agent can access views
    try:
        # This will fail without API keys, but we can test the initialization
        agent = SQLAgent.__new__(SQLAgent)
        agent.use_openai = True
        agent.table_schema = agent._get_table_schema()
        agent.view_manager = ViewManager()
        agent.available_views = agent.view_manager.get_views_for_agent()
        
        print(f"✅ Agent has access to {len(agent.available_views)} views")
        
        # Test system prompt includes views
        prompt = agent._create_system_prompt()
        for view in views:
            if f"VIEW: {view['name']}" in prompt:
                print(f"✅ View '{view['name']}' found in system prompt")
            else:
                print(f"❌ View '{view['name']}' NOT found in system prompt")
        
        # Test a simple query that would use views
        test_query = "SELECT * FROM interactions_per_day"
        print(f"🔍 Testing query: {test_query}")
        
        try:
            results = agent.execute_query(test_query)
            print(f"✅ View query executed successfully! Got {len(results)} rows")
            
            if results:
                print("Sample result:")
                print(results[0])
                
        except Exception as e:
            print(f"❌ View query failed: {e}")
            
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")

if __name__ == "__main__":
    test_view_integration()