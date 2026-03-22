#!/usr/bin/env python3
"""
Ollama Web Chat Service

A web-based chat interface for Ollama models using Flask.
Provides a simple web UI for chatting with locally running models.
"""

from flask import Flask, render_template, request, jsonify, stream_with_context, Response
import ollama
import json
import os
import os
from typing import List, Dict, Any, Generator
from tavily import TavilyClient

app = Flask(__name__)

class OllamaWebChat:
    """Web-based chat interface for Ollama models."""
    
    def __init__(self):
        self.client = ollama.Client()
        self.current_model = None
        self.messages: List[Dict[str, str]] = []
        self.tavily_client = None
        self._init_tavily()
    
    def _init_tavily(self):
        """Initialize Tavily client if API key is available."""
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            try:
                self.tavily_client = TavilyClient(api_key=tavily_api_key)
                print("✓ Tavily client initialized successfully")
            except Exception as e:
                print(f"✗ Failed to initialize Tavily client: {e}")
                self.tavily_client = None
        else:
            print("⚠ TAVILY_API_KEY not found in environment variables")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with details by calling ollama list."""
        try:
            # This directly calls the ollama list command equivalent
            models = self.client.list()
            available_models = []
            
            # Handle the Ollama ListResponse object
            if hasattr(models, 'models'):
                for model in models.models:
                    available_models.append({
                        'name': model.model,
                        'size': model.size,
                        'modified': model.modified_at.strftime('%Y-%m-%d %H:%M:%S') if model.modified_at else 'Unknown'
                    })
            elif isinstance(models, dict) and 'models' in models:
                for model in models['models']:
                    available_models.append({
                        'name': model['name'],
                        'size': model.get('size', 0),
                        'modified': 'Unknown'
                    })
            elif isinstance(models, list):
                for model in models:
                    available_models.append({
                        'name': model['name'],
                        'size': model.get('size', 0),
                        'modified': 'Unknown'
                    })
            
            return available_models
        except Exception as e:
            print(f"Error getting available models: {e}")
            return []
    
    def set_model(self, model_name: str) -> bool:
        """Set the current model."""
        available_models = [m['name'] for m in self.get_available_models()]
        if model_name in available_models:
            self.current_model = model_name
            self.clear_history()
            return True
        return False
    
    def _should_use_tavily(self, message: str) -> bool:
        """Determine if Tavily search is needed for the message."""
        if not self.tavily_client:
            print("ℹ️  Tavily client not available (no API key)")
            return False
        
        # Keywords that typically require up-to-date information
        search_keywords = [
            'latest', 'recent', 'current', 'today', 'now', '2024', '2025', '2026',
            'news', 'update', 'happening', 'what is', 'when is', 'where is',
            'how many', 'statistics', 'data', 'facts', 'research', 'study',
            'weather', 'temperature', 'stock', 'price', 'news', 'event', 'happening'
        ]
        
        # Check if message contains search-related keywords
        message_lower = message.lower()
        found_keywords = []
        for keyword in search_keywords:
            if keyword in message_lower:
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"🔍 Found search keywords: {', '.join(found_keywords)}")
            return True
        
        # Check for question patterns that might need current info
        question_patterns = [
            'what happened', 'what is happening', 'when did', 'where did',
            'how much', 'how many', 'latest news', 'current status',
            'what was the weather', 'what is the weather', 'stock price',
            'current temperature', 'latest update', 'recent news'
        ]
        
        for pattern in question_patterns:
            if pattern in message_lower:
                print(f"🔍 Found question pattern: '{pattern}'")
                return True
        
        # Check for date-specific queries that might need current information
        import datetime
        current_year = datetime.datetime.now().year
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # If message contains current year or date, likely needs up-to-date info
        if str(current_year) in message or current_date in message:
            print(f"📅 Found current date/year: {current_date} or {current_year}")
            return True
        
        print("ℹ️  No search keywords or patterns found - proceeding without Tavily")
        return False
    
    def _search_with_tavily(self, query: str) -> str:
        """Perform search using Tavily and return results."""
        try:
            # Perform search with Tavily
            search_result = self.tavily_client.search(
                query=query,
                search_depth="advanced",  # Use advanced search for better results
                max_results=5  # Limit to 5 results to keep response concise
            )
            
            # Format search results
            if search_result and 'results' in search_result:
                formatted_results = []
                for i, result in enumerate(search_result['results'][:3], 1):  # Show top 3 results
                    formatted_results.append(
                        f"Source {i}: {result.get('title', 'No title')}\n"
                        f"URL: {result.get('url', 'No URL')}\n"
                        f"Content: {result.get('content', 'No content')[:500]}..."
                    )
                
                return "\n\n".join(formatted_results)
            else:
                return "No search results found."
                
        except Exception as e:
            print(f"Error during Tavily search: {e}")
            return f"Search failed: {str(e)}"
    
    def chat_stream(self, message: str) -> Generator[str, None, None]:
        """Stream chat response from the model with optional Tavily search."""
        if not self.current_model:
            yield json.dumps({"error": "No model selected"}) + "\n"
            return
        
        try:
            print(f"\n📨 User message: {message}")
            
            # Add user message to conversation history
            self.messages.append({
                'role': 'user',
                'content': message
            })
            
            # Check if Tavily search is needed
            should_search = self._should_use_tavily(message)
            search_results = ""
            
            if should_search:
                print("🚀 Initiating Tavily search...")
                # Inform user about search
                yield json.dumps({
                    "type": "content",
                    "content": "🔍 Searching for up-to-date information..."
                }) + "\n"
                
                # Perform search
                search_results = self._search_with_tavily(message)
                print(f"✅ Tavily search completed")
                
                # Add search results to context
                self.messages.append({
                    'role': 'system',
                    'content': f"Search results for user query: {search_results}"
                })
                print(f"📚 Added {len(search_results)} characters of search results to context")
            else:
                print("⏭️  Skipping Tavily search - proceeding with direct response")
            
            # Get streaming response from model
            full_response = ""
            print("🤖 Generating AI response...")
            
            for chunk in self.client.chat(
                model=self.current_model,
                messages=self.messages,
                stream=True,
                options={
                    'num_ctx': 4096,  # Context window size
                    'num_predict': 2048,  # Max tokens to generate
                    'temperature': 0.7,  # Creativity level
                    'top_p': 0.9,  # Nucleus sampling
                    'repeat_penalty': 1.1,  # Repetition penalty
                }
            ):
                # Handle regular content
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    full_response += content
                    
                    # Yield each chunk as JSON for real-time streaming
                    yield json.dumps({
                        "type": "content",
                        "content": content
                    }) + "\n"
            
            # Store the full response in conversation history
            self.messages.append({
                'role': 'assistant',
                'content': full_response
            })
            
            print(f"✅ AI response completed ({len(full_response)} characters)")
            
            # Yield completion message
            yield json.dumps({
                "type": "complete",
                "content": full_response
            }) + "\n"
            
        except Exception as e:
            error_msg = f"Error during chat: {str(e)}"
            print(f"❌ Error: {error_msg}")
            yield json.dumps({
                "type": "error",
                "content": error_msg
            }) + "\n"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.messages = []


# Initialize chat instance
chat_instance = OllamaWebChat()


@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')


@app.route('/api/models')
def get_models():
    """Get list of available models."""
    models = chat_instance.get_available_models()
    return jsonify({
        "models": models,
        "current_model": chat_instance.current_model
    })


@app.route('/api/set_model', methods=['POST'])
def set_model():
    """Set the current model."""
    data = request.get_json()
    model_name = data.get('model_name')
    
    if chat_instance.set_model(model_name):
        return jsonify({
            "success": True,
            "message": f"Model set to {model_name}",
            "current_model": model_name
        })
    else:
        return jsonify({
            "success": False,
            "message": f"Model {model_name} not found"
        }), 400


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with streaming response."""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Return streaming response
    return Response(
        stream_with_context(chat_instance.chat_stream(message)),
        mimetype='application/json'
    )


@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history."""
    chat_instance.clear_history()
    return jsonify({
        "success": True,
        "message": "Conversation history cleared"
    })


@app.route('/api/status')
def get_status():
    """Get current chat status."""
    return jsonify({
        "current_model": chat_instance.current_model,
        "message_count": len(chat_instance.messages),
        "has_model": chat_instance.current_model is not None
    })


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Starting Ollama Web Chat Service...")
    print("Available at: http://localhost:5000")
    print("Make sure Ollama is running on your machine.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)