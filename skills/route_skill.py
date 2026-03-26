import json
import os
from typing import Dict, Any, List
import ollama


def route_skill(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses LLM to analyze user queries and determine which skill should be executed.
    
    Args:
        parameters: Dictionary containing:
            - user_query (str): The user's query or message
            - available_skills (list): List of available skills with their descriptions
            - conversation_history (list, optional): Recent conversation history for context
    
    Returns:
        Dictionary containing:
            - success (bool): Whether the routing was successful
            - selected_skill (str): The name of the skill to execute
            - confidence (float): Confidence score (0.0 to 1.0) of the selection
            - reasoning (str): Explanation for why this skill was selected
            - parameters (dict): Suggested parameters for the selected skill
            - message (str): Human-readable status message
    """
    try:
        # Extract parameters
        user_query = parameters.get('user_query', '')
        available_skills = parameters.get('available_skills', [])
        conversation_history = parameters.get('conversation_history', [])
        
        # Validate required parameters
        if not user_query:
            return {
                "success": False,
                "selected_skill": None,
                "confidence": 0.0,
                "reasoning": "",
                "parameters": {},
                "message": "No user query provided"
            }
        
        if not available_skills:
            return {
                "success": False,
                "selected_skill": None,
                "confidence": 0.0,
                "reasoning": "",
                "parameters": {},
                "message": "No available skills provided"
            }
        
        # Prepare skills information for the prompt
        skills_info = []
        for skill in available_skills:
            skills_info.append(f"- {skill['name']}: {skill['description']}")
        
        skills_text = "\n".join(skills_info)
        
        # Prepare conversation history context
        history_context = ""
        if conversation_history:
            history_lines = []
            for msg in conversation_history[-3:]:  # Use last 3 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_lines.append(f"{role}: {content}")
            history_context = "\n".join(history_lines)
        
        # Create the prompt for skill routing
        prompt = """You are an intelligent skill routing assistant. Your task is to analyze user queries and determine which skill should be executed.

Available skills:
{skills_text}

User query: "{user_query}"

{history_context_str}

Please analyze this query and determine:
1. Which skill (if any) should be executed
2. Your confidence in this decision (0.0 to 1.0)
3. Your reasoning for this selection
4. What parameters should be passed to the skill

Respond with a JSON object containing:
{{
    "selected_skill": "skill_name or null",
    "confidence": 0.0 to 1.0,
    "reasoning": "your explanation",
    "parameters": {{"param1": "value1", "param2": "value2"}},
    "should_execute_skill": true or false
}}

Rules:
- If no skill is appropriate, set selected_skill to null and should_execute_skill to false
- Only suggest skills that are in the available skills list
- Provide specific, actionable parameters
- Confidence should reflect how certain you are about the skill choice
- Reasoning should explain why this skill is the best match

IMPORTANT: Analyze the user query carefully and match it against the skill descriptions. Look for:
- Explicit requests for specific actions (e.g., "list files", "read file", "execute command")
- Keywords that indicate file operations (list, read, write, search, execute)
- Commands that should be run in shell
- Questions about current information that require web search
- Context clues that indicate the user's intent

Examples:
- "List files in current directory" → list_files skill
- "Read the content of config.json" → read_file skill  
- "Execute ls -la command" → execute_command skill
- "What's the latest news about AI?" → tavily_search skill""".format(
            skills_text=skills_text,
            user_query=user_query,
            history_context_str=history_context if history_context else "No conversation history available."
        )
        
        # Try to use LLM for analysis first
        try:
            # Get current model from environment or use a default
            current_model = os.getenv('OLLAMA_MODEL', 'qwen3.5:2b')
            
            # Call the LLM with the prompt
            response = ollama.generate(
                model=current_model,
                prompt=prompt,
                format='json',
                options={
                    'temperature': 0.1,  # Low temperature for more deterministic responses
                    'num_predict': 512,   # Limit response length
                }
            )
            
            # Parse the LLM response
            if response and 'response' in response:
                llm_output = response['response']
                
                # Try to parse JSON from response
                try:
                    result = json.loads(llm_output)
                    
                    # Validate the response structure
                    if 'selected_skill' in result and 'confidence' in result:
                        return {
                            "success": True,
                            "selected_skill": result.get("selected_skill"),
                            "confidence": result.get("confidence", 0.5),
                            "reasoning": result.get("reasoning", "LLM-based analysis"),
                            "parameters": result.get("parameters", {}),
                            "message": f"LLM skill routing completed with confidence {result.get('confidence', 0.5):.2f}"
                        }
                except json.JSONDecodeError:
                    # If JSON parsing fails, fall back to keyword analysis
                    pass
                    
        except Exception as llm_error:
            # If LLM call fails, fall back to keyword analysis
            print(f"LLM analysis failed: {llm_error}")
        
        # Fallback to keyword-based analysis
        query_lower = user_query.lower().strip()
        
        # Analyze query for skill matching
        skill_analysis = _analyze_query_for_skills(query_lower, available_skills)
        
        return {
            "success": True,
            "selected_skill": skill_analysis["selected_skill"],
            "confidence": skill_analysis["confidence"],
            "reasoning": skill_analysis["reasoning"],
            "parameters": skill_analysis["parameters"],
            "message": f"Skill routing completed with confidence {skill_analysis['confidence']:.2f}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "selected_skill": None,
            "confidence": 0.0,
            "reasoning": "",
            "parameters": {},
            "message": f"Error in skill routing: {str(e)}"
        }


def _analyze_query_for_skills(query: str, available_skills: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Analyze query and match against available skills using keyword patterns.
    This is a simplified version - in production, this would use LLM analysis.
    """
    # Define skill matching patterns
    skill_patterns = {
        'list_files': [
            'list files', 'list file', 'files in', 'file in', 'directory', 'folder',
            'show files', 'show file', 'what files', 'which files', 'ls ', 'dir '
        ],
        'read_file': [
            'read file', 'read files', 'open file', 'open files', 'show content',
            'show contents', 'cat ', 'type ', 'head ', 'tail '
        ],
        'write_file': [
            'write file', 'write files', 'create file', 'create files', 'save file',
            'save files', 'write content', 'write text', 'echo ', 'touch '
        ],
        'execute_command': [
            'run command', 'execute command', 'shell command', 'bash command',
            'linux command', 'terminal command', 'command ', 'cd ', 'mkdir ', 'rm ',
            'cp ', 'mv ', 'grep ', 'find ', 'pwd', 'whoami', 'ps ', 'top'
        ],
        'search_files': [
            'search file', 'search files', 'find file', 'find files', 'grep ',
            'rgrep', 'search content', 'search text', 'look for'
        ],
        'tavily_search': [
            'latest', 'recent', 'current', 'today', 'now', 'news', 'update',
            'weather', 'temperature', 'stock', 'price', 'what is', 'when is',
            'where is', 'how many', 'statistics', 'data', 'facts', 'research'
        ]
    }
    
    # Score each skill based on keyword matches
    skill_scores = {}
    
    for skill in available_skills:
        skill_name = skill['name']
        skill_desc = skill['description'].lower()
        
        score = 0.0
        
        # Check direct skill name matches
        if skill_name in query:
            score += 0.8
        
        # Check description matches
        if any(word in skill_desc for word in ['file', 'directory', 'folder'] if word in query):
            score += 0.3
        
        # Check pattern matches
        if skill_name in skill_patterns:
            for pattern in skill_patterns[skill_name]:
                if pattern in query:
                    score += 0.4
        
        skill_scores[skill_name] = score
    
    # Find the best match
    if not skill_scores or max(skill_scores.values()) == 0:
        return {
            "selected_skill": None,
            "confidence": 0.0,
            "reasoning": "No suitable skill found for this query",
            "parameters": {}
        }
    
    best_skill = max(skill_scores, key=skill_scores.get)
    confidence = min(skill_scores[best_skill] / 2.0, 1.0)  # Normalize confidence
    
    # Generate reasoning
    reasoning = f"Selected {best_skill} based on query analysis. Confidence: {confidence:.2f}"
    
    # Generate suggested parameters
    parameters = _generate_skill_parameters(query, best_skill)
    
    return {
        "selected_skill": best_skill,
        "confidence": confidence,
        "reasoning": reasoning,
        "parameters": parameters
    }


def _generate_skill_parameters(query: str, skill_name: str) -> Dict[str, Any]:
    """
    Generate suggested parameters for the selected skill based on query analysis.
    """
    parameters = {}
    
    if skill_name == 'list_files':
        # Look for path patterns
        import re
        path_match = re.search(r'["\']([^"\']+)["\']', query)
        if path_match:
            parameters['path'] = path_match.group(1)
        elif 'current' in query or '.' in query:
            parameters['path'] = '.'
        else:
            parameters['path'] = '.'
        parameters['recursive'] = 'recursive' in query or 'all' in query
    
    elif skill_name == 'read_file':
        # Look for file path patterns
        import re
        path_match = re.search(r'["\']([^"\']+)["\']', query)
        if path_match:
            parameters['path'] = path_match.group(1)
        parameters['max_lines'] = 100 if 'first' in query else 1000
    
    elif skill_name == 'write_file':
        # Look for file path and content
        import re
        path_match = re.search(r'["\']([^"\']+)["\']', query)
        if path_match:
            parameters['path'] = path_match.group(1)
        # Simple content extraction - in practice, this would be more sophisticated
        if 'hello' in query:
            parameters['content'] = 'Hello World'
        elif 'test' in query:
            parameters['content'] = 'Test content'
    
    elif skill_name == 'execute_command':
        # Extract command from query
        import re
        cmd_match = re.search(r'["\']([^"\']+)["\']', query)
        if cmd_match:
            parameters['command'] = cmd_match.group(1)
        else:
            # Try to extract command words
            command_words = []
            for word in query.split():
                if word not in ['run', 'execute', 'command', 'shell', 'bash', 'linux', 'terminal']:
                    command_words.append(word)
            if command_words:
                parameters['command'] = ' '.join(command_words)
        parameters['timeout'] = 30000
    
    elif skill_name == 'search_files':
        # Extract search pattern
        import re
        pattern_match = re.search(r'["\']([^"\']+)["\']', query)
        if pattern_match:
            parameters['pattern'] = pattern_match.group(1)
        else:
            parameters['pattern'] = '.*'
        parameters['recursive'] = True
    
    elif skill_name == 'tavily_search':
        # Use the query as search query
        parameters['query'] = query
        parameters['search_depth'] = 'advanced' if 'latest' in query or 'recent' in query else 'basic'
        parameters['max_results'] = 5
    
    return parameters