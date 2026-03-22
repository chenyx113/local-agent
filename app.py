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
import importlib.util
import sys
from pathlib import Path

app = Flask(__name__)

class OllamaWebChat:
    """Web-based chat interface for Ollama models."""
    
    def __init__(self):
        self.client = ollama.Client()
        self.current_model = None
        self.messages: List[Dict[str, str]] = []
        self.tavily_client = None
        self._init_tavily()
        self._init_skills()
    
    def _init_skills(self):
        """Initialize the skills system."""
        self.skills = {}
        self.skill_descriptions = {}
        
        # Load skills from the skills directory
        skills_dir = Path(__file__).parent / "skills"
        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.py"):
                if skill_file.name == "__init__.py":
                    continue
                
                skill_name = skill_file.stem
                try:
                    # Load the skill module
                    spec = importlib.util.spec_from_file_location(skill_name, skill_file)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[skill_name] = module
                    spec.loader.exec_module(module)
                    
                    # Find the skill function (should be the only function in the module)
                    skill_function = None
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if callable(attr) and not attr_name.startswith('_') and attr_name != 'Path' and attr_name != 'List' and attr_name != 'Dict' and attr_name != 'Any':
                            skill_function = attr
                            break
                    
                    if skill_function:
                        self.skills[skill_name] = skill_function
                        
                        # Load skill description from markdown file
                        md_file = skills_dir / f"{skill_name}.md"
                        if md_file.exists():
                            with open(md_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Extract description from markdown
                                lines = content.split('\n')
                                description = ""
                                for line in lines:
                                    if line.startswith('## Description'):
                                        # Get the next non-empty line as description
                                        for i, next_line in enumerate(lines[lines.index(line)+1:], 1):
                                            if next_line.strip():
                                                description = next_line.strip()
                                                break
                                        break
                                self.skill_descriptions[skill_name] = description or f"Skill: {skill_name}"
                    
                    print(f"✓ Loaded skill: {skill_name}")
                    
                except Exception as e:
                    print(f"✗ Failed to load skill {skill_name}: {e}")
        
        print(f"✓ Initialized {len(self.skills)} skills")
    
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
        
        # Convert message to lowercase for analysis
        message_lower = message.lower()
        
        # Check for file system operation keywords - these should NOT trigger Tavily search
        file_system_keywords = [
            'list files', 'list file', 'files in', 'file in', 'directory', 'folder',
            'path', 'directory', 'directories', 'folders', 'files', 'file',
            'read file', 'read files', 'write file', 'write files', 'search file',
            'search files', 'execute command', 'run command', 'shell command',
            'linux command', 'bash command', 'command', 'cd ', 'ls ', 'cat ', 'grep ',
            'find ', 'pwd', 'mkdir', 'rm ', 'cp ', 'mv ', 'touch ', 'echo '
        ]
        
        # Check if this is a file system operation
        for keyword in file_system_keywords:
            if keyword in message_lower:
                print(f"📁 Found file system keyword: '{keyword}' - skipping Tavily search")
                return False
        
        # Check for explicit path patterns (like /home/user/path)
        import re
        path_pattern = r'[/~][\w/.-]+'
        if re.search(path_pattern, message):
            print("📁 Found file path pattern - skipping Tavily search")
            return False
        
        # Keywords that typically require up-to-date information
        search_keywords = [
            'latest', 'recent', 'current', 'today', 'now', '2024', '2025', '2026',
            'news', 'update', 'happening', 'what is', 'when is', 'where is',
            'how many', 'statistics', 'data', 'facts', 'research', 'study',
            'weather', 'temperature', 'stock', 'price', 'news', 'event', 'happening'
        ]
        
        # Check if message contains search-related keywords
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
    
    def chat_stream(self, message: str, options: Dict[str, Any] = None) -> Generator[str, None, None]:
        """Stream chat response from the model with intelligent skill routing."""
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
            
            # Use intelligent skill routing to determine if we should use a skill
            skill_routing_result = self._route_skill(message)
            
            if skill_routing_result["success"] and skill_routing_result["selected_skill"]:
                selected_skill = skill_routing_result["selected_skill"]
                confidence = skill_routing_result["confidence"]
                reasoning = skill_routing_result["reasoning"]
                parameters = skill_routing_result["parameters"]
                
                print(f"🎯 Skill routing: {selected_skill} (confidence: {confidence:.2f})")
                print(f"💭 Reasoning: {reasoning}")
                
                # Inform user about skill execution
                yield json.dumps({
                    "type": "content",
                    "content": f"🤖 Executing {selected_skill} skill..."
                }) + "\n"
                
                # Execute the selected skill
                skill_result = self.execute_skill(selected_skill, parameters)
                
                if skill_result["success"]:
                    # Add skill result to context
                    skill_output = self._format_skill_result(selected_skill, skill_result)
                    self.messages.append({
                        'role': 'system',
                        'content': f"Skill execution result: {skill_output}"
                    })
                    print(f"✅ Skill {selected_skill} executed successfully")
                else:
                    # Add error to context
                    error_msg = f"Skill {selected_skill} failed: {skill_result.get('message', 'Unknown error')}"
                    self.messages.append({
                        'role': 'system',
                        'content': error_msg
                    })
                    print(f"❌ Skill {selected_skill} failed: {error_msg}")
            
            # Get streaming response from model
            full_response = ""
            print("🤖 Generating AI response...")
            
            # Use provided options or default options
            if options is None:
                options = {
                    'num_ctx': 4096,  # Context window size
                    'num_predict': 2048,  # Max tokens to generate
                    'temperature': 0.7,  # Creativity level
                    'top_p': 0.9,  # Nucleus sampling
                    'repeat_penalty': 1.1,  # Repetition penalty
                }
            
            for chunk in self.client.chat(
                model=self.current_model,
                messages=self.messages,
                stream=True,
                options=options
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
    
    def get_skills_list(self) -> List[Dict[str, str]]:
        """Get list of available skills."""
        skills_list = []
        for skill_name, description in self.skill_descriptions.items():
            skills_list.append({
                'name': skill_name,
                'description': description
            })
        return sorted(skills_list, key=lambda x: x['name'])
    
    def execute_skill(self, skill_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a skill with the given parameters."""
        if skill_name not in self.skills:
            return {
                "success": False,
                "error": f"Skill '{skill_name}' not found",
                "message": f"Available skills: {', '.join(self.skills.keys())}"
            }
        
        try:
            skill_function = self.skills[skill_name]
            result = skill_function(parameters)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error executing skill '{skill_name}': {str(e)}"
            }
    
    def _route_skill(self, message: str) -> Dict[str, Any]:
        """Use intelligent skill routing to determine which skill to execute."""
        try:
            # Get available skills
            available_skills = self.get_skills_list()
            
            # If no skills available, return direct response
            if not available_skills:
                return {
                    "success": True,
                    "selected_skill": None,
                    "confidence": 0.0,
                    "reasoning": "No skills available",
                    "parameters": {}
                }
            
            # Use route_skill if available, otherwise fall back to keyword-based routing
            if 'route_skill' in self.skills:
                try:
                    route_result = self.skills['route_skill']({
                        'user_query': message,
                        'available_skills': available_skills,
                        'conversation_history': self.messages[-5:]  # Last 5 messages for context
                    })
                    
                    if route_result.get("success") and route_result.get("selected_skill"):
                        return {
                            "success": True,
                            "selected_skill": route_result["selected_skill"],
                            "confidence": route_result.get("confidence", 0.5),
                            "reasoning": route_result.get("reasoning", "LLM-based routing"),
                            "parameters": route_result.get("parameters", {})
                        }
                except Exception as e:
                    print(f"⚠️  Route skill failed: {e}")
            
            # Fallback to keyword-based routing
            return self._route_skill_fallback(message, available_skills)
            
        except Exception as e:
            return {
                "success": False,
                "selected_skill": None,
                "confidence": 0.0,
                "reasoning": f"Error in skill routing: {str(e)}",
                "parameters": {}
            }
    
    def _route_skill_fallback(self, message: str, available_skills: List[Dict[str, str]]) -> Dict[str, Any]:
        """Fallback keyword-based skill routing."""
        try:
            # Convert message to lowercase for analysis
            message_lower = message.lower()
            
            # Check for file system operation keywords
            file_system_keywords = [
                'list files', 'list file', 'files in', 'file in', 'directory', 'folder',
                'path', 'directory', 'directories', 'folders', 'files', 'file',
                'read file', 'read files', 'write file', 'write files', 'search file',
                'search files', 'execute command', 'run command', 'shell command',
                'linux command', 'bash command', 'command', 'cd ', 'ls ', 'cat ', 'grep ',
                'find ', 'pwd', 'mkdir', 'rm ', 'cp ', 'mv ', 'touch ', 'echo '
            ]
            
            # Check for explicit path patterns
            import re
            path_pattern = r'[/~][\w/.-]+'
            
            # Check for Tavily search keywords
            tavily_keywords = [
                'latest', 'recent', 'current', 'today', 'now', '2024', '2025', '2026',
                'news', 'update', 'happening', 'what is', 'when is', 'where is',
                'how many', 'statistics', 'data', 'facts', 'research', 'study',
                'weather', 'temperature', 'stock', 'price', 'news', 'event', 'happening'
            ]
            
            # Analyze the message
            skill_scores = {}
            
            for skill in available_skills:
                skill_name = skill['name']
                score = 0.0
                
                # Direct skill name matches
                if skill_name in message_lower:
                    score += 0.8
                
                # File system operations
                if skill_name in ['list_files', 'read_file', 'write_file', 'search_files', 'execute_command']:
                    for keyword in file_system_keywords:
                        if keyword in message_lower:
                            score += 0.4
                
                # Path patterns for file operations
                if skill_name in ['list_files', 'read_file', 'write_file', 'search_files'] and re.search(path_pattern, message):
                    score += 0.6
                
                # Tavily search
                if skill_name == 'tavily_search':
                    for keyword in tavily_keywords:
                        if keyword in message_lower:
                            score += 0.4
            
            # Find the best match
            if skill_scores and max(skill_scores.values()) > 0:
                best_skill = max(skill_scores, key=skill_scores.get)
                confidence = min(skill_scores[best_skill] / 2.0, 1.0)
                
                # Generate parameters based on skill
                parameters = self._generate_skill_parameters_fallback(message, best_skill)
                
                return {
                    "success": True,
                    "selected_skill": best_skill,
                    "confidence": confidence,
                    "reasoning": f"Keyword-based routing selected {best_skill}",
                    "parameters": parameters
                }
            else:
                return {
                    "success": True,
                    "selected_skill": None,
                    "confidence": 0.0,
                    "reasoning": "No suitable skill found",
                    "parameters": {}
                }
                
        except Exception as e:
            return {
                "success": False,
                "selected_skill": None,
                "confidence": 0.0,
                "reasoning": f"Error in fallback routing: {str(e)}",
                "parameters": {}
            }
    
    def _generate_skill_parameters_fallback(self, message: str, skill_name: str) -> Dict[str, Any]:
        """Generate parameters for skills using fallback method."""
        parameters = {}
        
        if skill_name == 'list_files':
            import re
            path_match = re.search(r'["\']([^"\']+)["\']', message)
            if path_match:
                parameters['path'] = path_match.group(1)
            elif 'current' in message or '.' in message:
                parameters['path'] = '.'
            else:
                parameters['path'] = '.'
            parameters['recursive'] = 'recursive' in message or 'all' in message
        
        elif skill_name == 'read_file':
            import re
            path_match = re.search(r'["\']([^"\']+)["\']', message)
            if path_match:
                parameters['path'] = path_match.group(1)
            parameters['max_lines'] = 100 if 'first' in message else 1000
        
        elif skill_name == 'write_file':
            import re
            path_match = re.search(r'["\']([^"\']+)["\']', message)
            if path_match:
                parameters['path'] = path_match.group(1)
            if 'hello' in message:
                parameters['content'] = 'Hello World'
            elif 'test' in message:
                parameters['content'] = 'Test content'
        
        elif skill_name == 'execute_command':
            import re
            cmd_match = re.search(r'["\']([^"\']+)["\']', message)
            if cmd_match:
                parameters['command'] = cmd_match.group(1)
            else:
                command_words = []
                for word in message.split():
                    if word not in ['run', 'execute', 'command', 'shell', 'bash', 'linux', 'terminal']:
                        command_words.append(word)
                if command_words:
                    parameters['command'] = ' '.join(command_words)
            parameters['timeout'] = 30000
        
        elif skill_name == 'search_files':
            import re
            pattern_match = re.search(r'["\']([^"\']+)["\']', message)
            if pattern_match:
                parameters['pattern'] = pattern_match.group(1)
            else:
                parameters['pattern'] = '.*'
            parameters['recursive'] = True
        
        elif skill_name == 'tavily_search':
            parameters['query'] = message
            parameters['search_depth'] = 'advanced' if 'latest' in message or 'recent' in message else 'basic'
            parameters['max_results'] = 5
        
        return parameters
    
    def _format_skill_result(self, skill_name: str, result: Dict[str, Any]) -> str:
        """Format skill execution result for context."""
        if not result["success"]:
            return f"Skill {skill_name} failed: {result.get('message', 'Unknown error')}"
        
        if skill_name == 'list_files':
            files = result.get('files', [])
            directories = result.get('directories', [])
            total_count = result.get('total_count', 0)
            return f"Listed {total_count} items: {len(files)} files, {len(directories)} directories"
        
        elif skill_name == 'read_file':
            content = result.get('content', '')
            total_lines = result.get('total_lines', 0)
            read_lines = result.get('read_lines', 0)
            return f"Read {read_lines}/{total_lines} lines from file"
        
        elif skill_name == 'write_file':
            file_path = result.get('file_path', '')
            file_size = result.get('file_size', 0)
            return f"Successfully wrote {file_size} bytes to {file_path}"
        
        elif skill_name == 'execute_command':
            stdout = result.get('stdout', '')
            stderr = result.get('stderr', '')
            return_code = result.get('return_code', 0)
            return f"Command executed with return code {return_code}. Output: {stdout[:200]}..."
        
        elif skill_name == 'search_files':
            results = result.get('results', [])
            total_matches = result.get('total_matches', 0)
            return f"Found {total_matches} matches in search"
        
        elif skill_name == 'tavily_search':
            results = result.get('results', [])
            total_results = result.get('total_results', 0)
            return f"Tavily search returned {total_results} results"
        
        return f"Skill {skill_name} executed successfully"


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


@app.route('/api/skills')
def get_skills():
    """Get list of available skills."""
    skills = chat_instance.get_skills_list()
    return jsonify({
        "skills": skills,
        "total_count": len(skills)
    })


@app.route('/api/skill/<skill_name>', methods=['POST'])
def execute_skill(skill_name):
    """Execute a specific skill with parameters."""
    data = request.get_json()
    parameters = data.get('parameters', {})
    
    result = chat_instance.execute_skill(skill_name, parameters)
    return jsonify(result)


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Starting Ollama Web Chat Service...")
    print("Available at: http://localhost:5000")
    print("Make sure Ollama is running on your machine.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)