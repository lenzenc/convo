#!/usr/bin/env python3
"""
Command-line interface for the conversation analytics project.
Allows users to ask natural language questions about the conversation data.
"""

import os
import sys
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint
from sql_agent import SQLAgent

# Load environment variables
load_dotenv()

# Reduce log noise for CLI
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

console = Console()


def display_banner():
    """Display the application banner."""
    banner = """
# 🗣️ Conversation Analytics Query Tool

Ask questions about your conversation data in plain English and get instant insights!
    """
    console.print(Markdown(banner))


def display_help():
    """Display help information with example queries."""
    help_text = """
## 📋 Example Questions You Can Ask

### 🔢 Counting & Statistics
- How many conversations are there?
- How many unique sessions do we have?
- What's the average number of interactions per session?

### 📅 Time-based Queries
- Show me conversations by date
- How many conversations happened today?
- What are the busiest hours for conversations?

### 👥 User & Location Analysis
- What are the most common user roles?
- Which locations have the most conversations?
- Show me conversations from team leads

### 💬 Content Analysis
- What questions contain the word 'inventory'?
- Show me conversations about customer service
- What are the most common action types?

### 🔍 Advanced Queries
- Which sessions had more than 5 interactions?
- What's the response time between questions and answers?
- Show me conversations with high RAG source scores
- How many conversations couldn't be answered?

### 🏪 Retail-Specific Queries
- What are the most common inventory questions?
- Show me all customer service related conversations
- Which stores have the most POS issues?
- What safety questions are being asked most?

## 💡 Commands
- Type your question and press Enter
- Type 'help' for this help message
- Type 'quit' or 'exit' to quit
- Type 'debug on' to show generated SQL queries
- Type 'debug off' to hide SQL queries
    """
    console.print(Markdown(help_text))


def format_results_as_table(results: List[Dict[str, Any]]) -> Table:
    """Format query results as a rich Table."""
    if not results:
        return None
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    
    # Add columns
    columns = list(results[0].keys())
    for col in columns:
        table.add_column(col)
    
    # Add rows
    for row in results:
        table.add_row(*[str(row.get(col, '')) for col in columns])
    
    return table


def format_results_as_markdown(results: List[Dict[str, Any]], question: str, sql_query: str = None, show_debug: bool = False) -> str:
    """Format query results as markdown."""
    if not results:
        return f"## 📭 No Results\n\n**Question:** {question}\n\nNo results found for your query."
    
    # Build markdown response
    markdown = f"## 📊 Query Results\n\n"
    markdown += f"**Question:** {question}\n\n"
    markdown += f"**Found {len(results)} result(s)**\n\n"
    
    # Add SQL query if debug mode is on
    if show_debug and sql_query:
        markdown += f"### 🔍 Generated SQL Query\n\n```sql\n{sql_query}\n```\n\n"
    
    return markdown


def initialize_agent() -> SQLAgent:
    """Initialize the SQL Agent."""
    try:
        # Check for API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_AI_API_KEY')
        
        if not openai_key and not google_key:
            console.print("❌ [red]No AI API keys found![/red]")
            console.print("Please set either [yellow]OPENAI_API_KEY[/yellow] or [yellow]GOOGLE_AI_API_KEY[/yellow] in your .env file.")
            sys.exit(1)
        
        # Initialize agent
        agent = SQLAgent()
        
        provider = "OpenAI GPT-4" if agent.use_openai else "Google Gemini"
        console.print(f"✅ [green]SQL Agent initialized successfully![/green]")
        console.print(f"Using [cyan]{provider}[/cyan] for query generation.\n")
        
        return agent
        
    except Exception as e:
        console.print(f"❌ [red]Failed to initialize SQL Agent:[/red] {str(e)}")
        sys.exit(1)


def process_query(agent: SQLAgent, question: str, show_debug: bool = False) -> None:
    """Process a natural language query and display results."""
    try:
        # Show processing message
        with console.status(f"[bold blue]Processing your question...[/bold blue]"):
            # Generate SQL (for debug display)
            sql_query = agent.generate_sql(question) if show_debug else None
            
            # Execute query
            results = agent.ask(question)
        
        # Display results
        if not results:
            console.print(f"📭 [yellow]No results found for:[/yellow] {question}")
            if show_debug and sql_query:
                console.print(f"\n[dim]Generated SQL:[/dim]\n```sql\n{sql_query}\n```")
            return
        
        # Show results summary
        console.print(f"\n📊 [bold green]Found {len(results)} result(s)[/bold green]")
        
        # Show debug info if enabled
        if show_debug and sql_query:
            console.print("\n🔍 [dim]Generated SQL Query:[/dim]")
            console.print(Panel(sql_query, title="SQL", border_style="dim"))
        
        # Display results as table
        table = format_results_as_table(results)
        if table:
            console.print("\n📋 [bold]Results:[/bold]")
            console.print(table)
        
        console.print()
        
    except Exception as e:
        console.print(f"❌ [red]Error processing your query:[/red] {str(e)}")
        console.print(f"💡 [yellow]Try rephrasing your question or asking something simpler.[/yellow]")
        if show_debug:
            console.print(f"[dim]Your question:[/dim] {question}")


def main():
    """Main CLI loop."""
    display_banner()
    
    # Initialize agent
    agent = initialize_agent()
    
    # Show initial help
    console.print("💡 Type [cyan]'help'[/cyan] for example questions, or start asking about your data!\n")
    
    # Debug mode flag
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            question = Prompt.ask("🤔 [bold blue]Your question[/bold blue]", default="").strip()
            
            if not question:
                continue
            
            # Handle special commands
            if question.lower() in ['quit', 'exit', 'q']:
                console.print("👋 [green]Goodbye![/green]")
                break
            elif question.lower() == 'help':
                display_help()
                continue
            elif question.lower() == 'debug on':
                debug_mode = True
                console.print("🔧 [yellow]Debug mode enabled - SQL queries will be shown[/yellow]")
                continue
            elif question.lower() == 'debug off':
                debug_mode = False
                console.print("🔧 [yellow]Debug mode disabled[/yellow]")
                continue
            
            # Process the query
            process_query(agent, question, debug_mode)
            
        except KeyboardInterrupt:
            console.print("\n👋 [green]Goodbye![/green]")
            break
        except Exception as e:
            console.print(f"❌ [red]Unexpected error:[/red] {str(e)}")


if __name__ == "__main__":
    main()