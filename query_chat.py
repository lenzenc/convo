#!/usr/bin/env python3
"""
Interactive query chat interface for the conversation analytics project.
Allows users to ask natural language questions about the conversation data.
"""

import os
import sys
import logging
from sql_agent import SQLAgent

logging.basicConfig(level=logging.WARNING)  # Reduce log noise for interactive use
logger = logging.getLogger(__name__)


def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("   Conversation Analytics - Natural Language Query Tool")
    print("=" * 60)
    print("Ask questions about your conversation data in plain English!")
    print("Examples:")
    print("  • How many conversations are there?")
    print("  • Show me conversations by date")
    print("  • What are the most common user actions?")
    print("  • How many sessions had more than 3 interactions?")
    print("  • What questions were asked about inventory?")
    print("\nType 'exit' or 'quit' to end the session.")
    print("Type 'help' for more examples.")
    print("-" * 60)


def print_help():
    """Print help with example queries."""
    print("\n📋 Example Questions You Can Ask:")
    print("\n🔢 Counting & Statistics:")
    print("  • How many conversations are there?")
    print("  • How many unique sessions do we have?")
    print("  • What's the average number of interactions per session?")
    
    print("\n📅 Time-based Queries:")
    print("  • Show me conversations by date")
    print("  • How many conversations happened today?")
    print("  • What are the busiest hours for conversations?")
    
    print("\n👥 User & Location Analysis:")
    print("  • What are the most common user roles?")
    print("  • Which locations have the most conversations?")
    print("  • Show me conversations from team leads")
    
    print("\n💬 Content Analysis:")
    print("  • What questions contain the word 'inventory'?")
    print("  • Show me conversations about customer service")
    print("  • What are the most common action types?")
    
    print("\n🔍 Advanced Queries:")
    print("  • Which sessions had more than 5 interactions?")
    print("  • What's the response time between questions and answers?")
    print("  • Show me conversations with high RAG source scores")
    print("-" * 60)


def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['OPENAI_API_KEY', 'GOOGLE_AI_API_KEY']
    available_vars = [var for var in required_vars if os.getenv(var)]
    
    if not available_vars:
        print("⚠️  No AI API keys found!")
        print("Please set one of the following environment variables:")
        print("   • OPENAI_API_KEY (for OpenAI GPT-4)")
        print("   • GOOGLE_AI_API_KEY (for Google Gemini)")
        print("\nExample:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    return True


def main():
    """Main interactive loop."""
    print_banner()
    
    # Check environment
    if not check_environment():
        return 1
    
    # Initialize the agent
    try:
        # Try OpenAI first, fall back to Google AI
        use_openai = bool(os.getenv('OPENAI_API_KEY'))
        if use_openai:
            print("🤖 Using OpenAI GPT-4 for query generation...")
        else:
            print("🤖 Using Google Gemini for query generation...")
        
        agent = SQLAgent(use_openai=use_openai)
        print("✅ SQL Agent initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize SQL Agent: {e}")
        return 1
    
    print("\n💡 Ready for your questions!\n")
    
    # Interactive loop
    while True:
        try:
            # Get user input
            question = input("🗣️  Your question: ").strip()
            
            # Handle special commands
            if question.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if question.lower() in ['help', 'h']:
                print_help()
                continue
            
            if not question:
                continue
            
            print(f"\n🔍 Processing: {question}")
            print("⏳ Generating SQL query...")
            
            # Get results from the agent
            results = agent.ask(question)
            
            # Display results
            if results:
                print("📊 Results:")
                print(agent.format_results(results))
                print(f"\n✅ Found {len(results)} result(s)")
            else:
                print("📭 No results found for your query.")
            
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try rephrasing your question or type 'help' for examples.")
            print("-" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())