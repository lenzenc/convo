#!/usr/bin/env python3
"""
Flask web interface for the conversation analytics project.
Lightweight alternative to Gradio that avoids Python 3.13 compatibility issues.
"""

import os
import logging
from flask import Flask, render_template_string, request, jsonify
import pandas as pd
from dotenv import load_dotenv
from sql_agent import SQLAgent

# Load environment variables
load_dotenv()

# Reduce log noise for web interface
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
agent = None

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversation Analytics Query Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
            padding: 30px;
            min-height: 600px;
        }
        
        .query-section {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .query-input {
            width: 100%;
            min-height: 120px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        .query-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
            flex: 2;
        }
        
        .btn-primary:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #f7fafc;
            color: #4a5568;
            border: 2px solid #e2e8f0;
            flex: 1;
        }
        
        .btn-secondary:hover {
            background: #edf2f7;
        }
        
        .status {
            padding: 15px;
            border-radius: 8px;
            background: #f0fff4;
            border: 1px solid #9ae6b4;
            color: #276749;
        }
        
        .results-section {
            border-left: 2px solid #e0e0e0;
            padding-left: 30px;
        }
        
        .results-content {
            background: #f8fafc;
            border-radius: 12px;
            padding: 20px;
            min-height: 500px;
            overflow-y: auto;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        
        .error {
            background: #fed7d7;
            border: 1px solid #fc8181;
            color: #c53030;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        th {
            background: #f7fafc;
            font-weight: 600;
            color: #2d3748;
        }
        
        .examples {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .examples h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .example-item {
            padding: 8px 0;
            cursor: pointer;
            transition: color 0.3s;
        }
        
        .example-item:hover {
            color: #667eea;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .results-section {
                border-left: none;
                border-top: 2px solid #e0e0e0;
                padding-left: 0;
                padding-top: 30px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗣️ Conversation Analytics</h1>
            <p>Ask questions about your conversation data in plain English</p>
        </div>
        
        <div class="main-content">
            <div class="query-section">
                <textarea 
                    id="queryInput" 
                    class="query-input" 
                    placeholder="Ask anything about your conversation data... e.g., 'How many conversations are there?'"
                ></textarea>
                
                <div class="button-group">
                    <button id="submitBtn" class="btn btn-primary">🔍 Ask Question</button>
                    <button id="clearBtn" class="btn btn-secondary">🗑️ Clear</button>
                </div>
                
                <div id="status" class="status">
                    Ready to answer your questions! Enter a question above to get started.
                </div>
                
                <div class="examples">
                    <h3>📋 Example Questions</h3>
                    <div class="example-item" onclick="setQuery('How many conversations are there?')">
                        • How many conversations are there?
                    </div>
                    <div class="example-item" onclick="setQuery('Show me conversations by date')">
                        • Show me conversations by date
                    </div>
                    <div class="example-item" onclick="setQuery('What are the most common user actions?')">
                        • What are the most common user actions?
                    </div>
                    <div class="example-item" onclick="setQuery('How many conversations couldn\\'t be answered?')">
                        • How many conversations couldn't be answered?
                    </div>
                    <div class="example-item" onclick="setQuery('What are the busiest hours for conversations?')">
                        • What are the busiest hours for conversations?
                    </div>
                </div>
            </div>
            
            <div class="results-section">
                <h2>📊 Query Results</h2>
                <div id="results" class="results-content">
                    <div style="text-align: center; padding: 40px; color: #718096;">
                        Results will appear here after you ask a question
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
        }
        
        function showLoading() {
            document.getElementById('results').innerHTML = '<div class="loading">⏳ Processing your question...</div>';
        }
        
        function showError(message) {
            document.getElementById('results').innerHTML = '<div class="error">' + message + '</div>';
        }
        
        function showResults(data) {
            if (data.error) {
                showError(data.error);
                return;
            }
            
            let html = '<h3>Question: ' + data.question + '</h3>';
            html += '<p><strong>Found ' + data.count + ' result(s)</strong></p>';
            
            if (data.results && data.results.length > 0) {
                html += data.table_html;
            }
            
            if (data.sql && data.sql.trim()) {
                html += '<details style="margin-top: 20px;"><summary><strong>🔍 Generated SQL Query</strong></summary>';
                html += '<pre style="background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 8px; margin-top: 10px; overflow-x: auto;"><code>' + data.sql + '</code></pre>';
                html += '</details>';
            }
            
            document.getElementById('results').innerHTML = html;
        }
        
        async function submitQuery() {
            const query = document.getElementById('queryInput').value.trim();
            
            if (!query) {
                showError('Please enter a question');
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: query })
                });
                
                const data = await response.json();
                showResults(data);
                
            } catch (error) {
                showError('Network error: ' + error.message);
            }
        }
        
        function clearQuery() {
            document.getElementById('queryInput').value = '';
            document.getElementById('results').innerHTML = '<div style="text-align: center; padding: 40px; color: #718096;">Results will appear here after you ask a question</div>';
        }
        
        // Event listeners
        document.getElementById('submitBtn').addEventListener('click', submitQuery);
        document.getElementById('clearBtn').addEventListener('click', clearQuery);
        
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                submitQuery();
            }
        });
        
        // Initialize agent status
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').innerHTML = data.message;
                if (!data.success) {
                    document.getElementById('status').style.background = '#fed7d7';
                    document.getElementById('status').style.borderColor = '#fc8181';
                    document.getElementById('status').style.color = '#c53030';
                }
            });
    </script>
</body>
</html>
"""


def initialize_agent():
    """Initialize the SQL Agent and return status."""
    global agent
    
    try:
        # Check for API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_AI_API_KEY')
        
        if not openai_key and not google_key:
            return False, "❌ No AI API keys found! Please set either OPENAI_API_KEY or GOOGLE_AI_API_KEY in your .env file."
        
        # Initialize agent
        agent = SQLAgent()
        
        provider = "OpenAI GPT-4" if agent.use_openai else "Google Gemini"
        return True, f"✅ SQL Agent initialized successfully! Using {provider} for query generation."
        
    except Exception as e:
        return False, f"❌ Failed to initialize SQL Agent: {str(e)}"


@app.route('/')
def index():
    """Serve the main interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/status')
def status():
    """Get agent initialization status."""
    success, message = initialize_agent()
    return jsonify({'success': success, 'message': message})


@app.route('/query', methods=['POST'])
def query():
    """Process a natural language query."""
    global agent
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Please enter a question'})
        
        if not agent:
            success, message = initialize_agent()
            if not success:
                return jsonify({'error': message})
        
        # Process the query
        results = agent.ask(question)
        
        response = {
            'question': question,
            'results': results,
            'count': len(results) if results else 0
        }
        
        # Format results as HTML table
        if results:
            df = pd.DataFrame(results)
            response['table_html'] = df.to_html(classes='table', table_id='results-table', index=False)
        
        # Add SQL query if in debug mode
        if os.getenv('DEBUG_MODE', 'False').lower() == 'true':
            try:
                response['sql'] = agent.generate_sql(question)
            except:
                pass
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Error processing query: {str(e)}'})


def main():
    """Launch the Flask interface."""
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    print("🚀 Starting Conversation Analytics Query Tool...")
    print(f"📍 Server: http://{host}:{port}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()