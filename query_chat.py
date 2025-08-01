#!/usr/bin/env python3
"""
Gradio web interface for the conversation analytics project.
Allows users to ask natural language questions about the conversation data through a web UI.
"""

import os
import logging
import gradio as gr
import pandas as pd
from typing import Tuple
from dotenv import load_dotenv
from sql_agent import SQLAgent

# Load environment variables
load_dotenv()

# Reduce log noise for web interface
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Global agent instance
agent = None


def initialize_agent() -> Tuple[bool, str]:
    """Initialize the SQL Agent and return status."""
    global agent
    
    try:
        # Check for API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_AI_API_KEY')
        
        if not openai_key and not google_key:
            return False, "❌ **No AI API keys found!**\n\nPlease set either `OPENAI_API_KEY` or `GOOGLE_AI_API_KEY` in your `.env` file."
        
        # Initialize agent
        agent = SQLAgent()
        
        provider = "OpenAI GPT-4" if agent.use_openai else "Google Gemini"
        return True, f"✅ **SQL Agent initialized successfully!**\n\nUsing {provider} for query generation."
        
    except Exception as e:
        return False, f"❌ **Failed to initialize SQL Agent:**\n\n```\n{str(e)}\n```"


def process_query(question: str) -> str:
    """Process a natural language query and return formatted results."""
    global agent
    
    if not agent:
        success, message = initialize_agent()
        if not success:
            return message
    
    if not question.strip():
        return "💭 **Please enter a question about your conversation data.**"
    
    try:
        # Process the query
        results = agent.ask(question)
        
        if not results:
            return f"📭 **No results found for your query.**\n\n**Question:** {question}"
        
        # Format results as markdown
        markdown_result = f"## 📊 Query Results\n\n"
        markdown_result += f"**Question:** {question}\n\n"
        markdown_result += f"**Found {len(results)} result(s)**\n\n"
        
        # Convert results to DataFrame for better formatting
        df = pd.DataFrame(results)
        
        # Format as markdown table
        markdown_result += df.to_markdown(index=False, tablefmt="github")
        
        # Add SQL query information if in debug mode
        if os.getenv('DEBUG_MODE', 'False').lower() == 'true':
            try:
                sql_query = agent.generate_sql(question)
                markdown_result += f"\n\n### 🔍 Generated SQL Query\n\n```sql\n{sql_query}\n```"
            except:
                pass
        
        return markdown_result
        
    except Exception as e:
        error_msg = f"❌ **Error processing your query:**\n\n```\n{str(e)}\n```\n\n"
        error_msg += "💡 **Try:**\n"
        error_msg += "- Rephrasing your question\n"
        error_msg += "- Using simpler language\n"
        error_msg += "- Asking about basic statistics first\n\n"
        error_msg += f"**Your question:** {question}"
        return error_msg


def get_example_queries() -> str:
    """Return example queries as markdown."""
    return """
# 📋 Example Questions You Can Ask

## 🔢 Counting & Statistics
- How many conversations are there?
- How many unique sessions do we have?
- What's the average number of interactions per session?

## 📅 Time-based Queries
- Show me conversations by date
- How many conversations happened today?
- What are the busiest hours for conversations?

## 👥 User & Location Analysis
- What are the most common user roles?
- Which locations have the most conversations?
- Show me conversations from team leads

## 💬 Content Analysis
- What questions contain the word 'inventory'?
- Show me conversations about customer service
- What are the most common action types?

## 🔍 Advanced Queries
- Which sessions had more than 5 interactions?
- What's the response time between questions and answers?
- Show me conversations with high RAG source scores
- How many conversations couldn't be answered?

## 🏪 Retail-Specific Queries
- What are the most common inventory questions?
- Show me all customer service related conversations
- Which stores have the most POS issues?
- What safety questions are being asked most?

*Click any example above to copy it to the input field, or type your own question!*
"""


def create_interface():
    """Create and configure the Gradio interface."""
    
    # Custom CSS for better styling
    css = """
    .gradio-container {
        max-width: 1200px !important;
    }
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 1em;
    }
    .query-input textarea {
        font-size: 16px !important;
        min-height: 100px !important;
    }
    .results-output {
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
        max-height: 600px;
        overflow-y: auto;
    }
    """
    
    with gr.Blocks(css=css, title="Conversation Analytics Query Tool") as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            🗣️ Conversation Analytics Query Tool
        </div>
        <p style="text-align: center; font-size: 1.1em; color: #666; margin-bottom: 2em;">
            Ask questions about your conversation data in plain English and get instant insights!
        </p>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Query input
                query_input = gr.Textbox(
                    label="💭 Your Question",
                    placeholder="Ask anything about your conversation data... e.g., 'How many conversations are there?'",
                    lines=3,
                    elem_classes=["query-input"]
                )
                
                # Buttons
                with gr.Row():
                    submit_btn = gr.Button("🔍 Ask Question", variant="primary", scale=2)
                    clear_btn = gr.Button("🗑️ Clear", scale=1)
                
                # Status/Info
                status_display = gr.Markdown(
                    value="🚀 **Ready to answer your questions!**\n\nEnter a question above to get started.",
                    visible=True
                )
            
            with gr.Column(scale=2):
                # Results display
                results_display = gr.Markdown(
                    label="📊 Query Results",
                    value=get_example_queries(),
                    elem_classes=["results-output"]
                )
        
        # Event handlers
        def handle_submit(question):
            if not question.strip():
                return "💭 **Please enter a question to get started.**", question
            
            # Show processing status
            processing_msg = f"⏳ **Processing your question...**\n\n*Question:* {question}\n\n*Please wait while I generate the SQL query and fetch results...*"
            
            # Process the query
            result = process_query(question)
            return result, question
        
        def handle_clear():
            return "", get_example_queries()
        
        # Connect events
        submit_btn.click(
            fn=handle_submit,
            inputs=[query_input],
            outputs=[results_display, query_input]
        )
        
        query_input.submit(
            fn=handle_submit,
            inputs=[query_input],
            outputs=[results_display, query_input]
        )
        
        clear_btn.click(
            fn=handle_clear,
            outputs=[query_input, results_display]
        )
        
        # Initialize agent on startup
        def on_startup():
            success, message = initialize_agent()
            return message
        
        interface.load(on_startup, outputs=[status_display])
    
    return interface


def main():
    """Launch the Gradio interface."""
    
    # Get configuration from environment
    server_name = os.getenv('GRADIO_SERVER_NAME', '127.0.0.1')
    server_port = int(os.getenv('GRADIO_SERVER_PORT', '7860'))
    share = os.getenv('GRADIO_SHARE', 'False').lower() == 'true'
    debug = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Create and launch interface
    interface = create_interface()
    
    print("🚀 Starting Conversation Analytics Query Tool...")
    print(f"📍 Server: http://{server_name}:{server_port}")
    
    if share:
        print("🌐 Public sharing enabled")
    
    interface.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        debug=debug,
        show_error=True,
        inbrowser=True
    )


if __name__ == "__main__":
    main()