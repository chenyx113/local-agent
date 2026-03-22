# Route Skill Skill

## Description
Uses LLM to analyze user queries and determine which skill should be executed.

## Purpose
This skill provides intelligent skill routing by using the LLM to analyze user queries and determine the most appropriate skill to execute. It replaces the keyword-based approach with a more sophisticated LLM-driven decision making process.

## Input Parameters
- **user_query** (string): The user's query or message
- **available_skills** (list): List of available skills with their descriptions
- **conversation_history** (list, optional): Recent conversation history for context

## Output
Returns a dictionary containing:
- **success** (boolean): Whether the routing was successful
- **selected_skill** (string): The name of the skill to execute
- **confidence** (float): Confidence score (0.0 to 1.0) of the selection
- **reasoning** (string): Explanation for why this skill was selected
- **parameters** (dict): Suggested parameters for the selected skill
- **message** (string): Human-readable status message

## Examples
```
User: "List files in the current directory"
Assistant: Uses route_skill to analyze the query and determines:
- selected_skill: "list_files"
- confidence: 0.95
- reasoning: "User is asking to list files, which matches the list_files skill purpose"
- parameters: {"path": ".", "recursive": false}

User: "What's the latest news about AI?"
Assistant: Uses route_skill to analyze the query and determines:
- selected_skill: "tavily_search"
- confidence: 0.90
- reasoning: "User is asking for latest news, which requires real-time information search"
- parameters: {"query": "latest news about AI", "search_depth": "advanced"}

User: "Run 'ls -la' command"
Assistant: Uses route_skill to analyze the query and determines:
- selected_skill: "execute_command"
- confidence: 0.98
- reasoning: "User is explicitly asking to run a shell command"
- parameters: {"command": "ls -la", "timeout": 30000}
```

## Implementation Notes
- Uses the current model to analyze the query and make skill selection decisions
- Considers both the query content and available skills descriptions
- Provides confidence scores to indicate selection certainty
- Includes reasoning for transparency and debugging
- Suggests appropriate parameters based on query analysis
- Falls back to direct response if no suitable skill is found
- Supports conversation history for better context understanding