#!/usr/bin/env python3
"""
Demo script showing the enhanced SQL Agent with view functionality.
Set OPENAI_API_KEY or GOOGLE_AI_API_KEY to test AI-powered query generation.
"""

import os
from sql_agent import SQLAgent

def demo_view_functionality():
    """Demonstrate how the enhanced SQL Agent uses views."""
    print("🚀 Enhanced SQL Agent with Views Demo\n")
    
    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if not openai_key and not google_key:
        print("⚠️  No API keys found. Set OPENAI_API_KEY or GOOGLE_AI_API_KEY to test AI functionality.")
        print("For now, showing direct view queries...\n")
        
        # Test direct view queries without AI
        agent = SQLAgent.__new__(SQLAgent)
        agent.use_openai = True
        agent.table_schema = agent._get_table_schema()
        agent.view_manager = agent.view_manager = __import__('view_manager').ViewManager()
        agent.available_views = agent.view_manager.get_views_for_agent()
        
        demo_queries = [
            ("Daily Interactions View", "SELECT * FROM interactions_per_day LIMIT 5"),
            ("Popular Actions View", "SELECT * FROM popular_actions LIMIT 3"),
            ("Active Sessions View", "SELECT * FROM active_sessions LIMIT 3"),
        ]
        
        for description, query in demo_queries:
            print(f"📊 {description}")
            print(f"Query: {query}")
            try:
                results = agent.execute_query(query)
                print(f"✅ Got {len(results)} results")
                if results:
                    print("Sample result:", results[0])
                print()
            except Exception as e:
                print(f"❌ Error: {e}\n")
    
    else:
        print("✅ API key found! Testing AI-powered view selection...")
        
        try:
            agent = SQLAgent()
            print(f"Using: {'OpenAI' if agent.use_openai else 'Google AI'}\n")
            
            # Test questions that should use views
            test_questions = [
                "Show me interactions per day",
                "What are the most popular actions?", 
                "Which sessions are most active?",
                "Show me recent activity"
            ]
            
            for question in test_questions:
                print(f"❓ Question: {question}")
                try:
                    sql = agent.generate_sql(question)
                    print(f"🔍 Generated SQL: {sql}")
                    
                    # Check if it uses a view
                    view_names = [view['name'] for view in agent.available_views]
                    uses_view = any(view_name in sql for view_name in view_names)
                    print(f"📈 Uses view: {'✅ Yes' if uses_view else '❌ No'}")
                    
                    # Execute the query
                    results = agent.execute_query(sql)
                    print(f"✅ Results: {len(results)} rows")
                    print()
                    
                except Exception as e:
                    print(f"❌ Error: {e}\n")
                    
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")

if __name__ == "__main__":
    demo_view_functionality()