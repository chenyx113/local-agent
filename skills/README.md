# Skills Directory

This directory contains skill definitions and implementations for the Ollama Web Chat service.

## Skill Structure

Each skill consists of:
- A markdown file (`.md`) containing the skill definition and documentation
- A Python file (`.py`) containing the skill implementation

## Available Skills

### 1. File System Skills
- **list_files.md/py** - List files in a directory
- **read_file.md/py** - Read content from a file
- **write_file.md/py** - Write content to a file
- **search_files.md/py** - Search files with regex patterns

### 2. System Skills
- **execute_command.md/py** - Execute shell commands
- **get_system_info.md/py** - Get system information

### 3. Utility Skills
- **datetime.md/py** - Get current date and time
- **weather.md/py** - Get weather information (requires API key)

## Skill Format

### Markdown File Format
```markdown
# Skill Name

## Description
Brief description of what this skill does.

## Purpose
Detailed explanation of the skill's purpose and use cases.

## Input Parameters
- **parameter_name** (type): Description of the parameter
- **optional_param** (type, optional): Description of optional parameter

## Output
Description of what the skill returns.

## Examples
```
User: "List files in /home/user/documents"
Assistant: Uses list_files skill with path="/home/user/documents"

User: "Read the content of config.json"
Assistant: Uses read_file skill with path="config.json"
```

## Implementation Notes
Any special considerations or limitations for this skill.
```

### Python File Format
```python
from typing import Dict, Any, List, Optional
import os
import subprocess
from datetime import datetime

def skill_function_name(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skill implementation function.
    
    Args:
        parameters: Dictionary containing input parameters
        
    Returns:
        Dictionary containing the result
    """
    try:
        # Skill implementation
        result = {
            "success": True,
            "data": "result data",
            "message": "Operation completed successfully"
        }
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Operation failed"
        }
```

## Creating New Skills

1. Create a markdown file with the skill definition
2. Create a Python file with the skill implementation
3. Ensure both files have the same base name
4. Follow the format guidelines above
5. Test the skill thoroughly

## Skill Activation Logic

The system uses intelligent skill routing to determine which skill to execute based on user queries:

### 1. File System Skills

#### list_files Skill
**Activation Triggers:**
- Keywords: "list files", "list file", "files in", "file in", "directory", "folder", "show files", "show file", "what files", "which files"
- Commands: "ls ", "dir "
- Path patterns: Queries containing file paths like "/home/user/path" or "~/documents"
- Examples:
  - "List files in the current directory"
  - "Show me what's in /home/user/documents"
  - "What files are in this folder?"

#### read_file Skill
**Activation Triggers:**
- Keywords: "read file", "read files", "open file", "open files", "show content", "show contents"
- Commands: "cat ", "type ", "head ", "tail "
- File references: Queries mentioning specific files or asking to view content
- Examples:
  - "Read the content of config.json"
  - "Show me the contents of main.py"
  - "Open and display the log file"

#### write_file Skill
**Activation Triggers:**
- Keywords: "write file", "write files", "create file", "create files", "save file", "save files", "write content", "write text"
- Commands: "echo ", "touch "
- Content creation: Queries asking to create or modify files
- Examples:
  - "Create a new file called notes.txt"
  - "Write 'Hello World' to output.txt"
  - "Save this configuration to settings.json"

#### search_files Skill
**Activation Triggers:**
- Keywords: "search file", "search files", "find file", "find files", "grep ", "rgrep", "search content", "search text", "look for"
- Content search: Queries asking to find specific content or patterns in files
- Examples:
  - "Search for TODO comments in the codebase"
  - "Find all function definitions in JavaScript files"
  - "Look for error messages in log files"

### 2. System Skills

#### execute_command Skill
**Activation Triggers:**
- Keywords: "run command", "execute command", "shell command", "bash command", "linux command", "terminal command"
- Commands: "cd ", "mkdir ", "rm ", "cp ", "mv ", "grep ", "find ", "pwd", "whoami", "ps ", "top"
- System operations: Queries asking to run specific commands or perform system tasks
- Examples:
  - "Run 'ls -la' command"
  - "Execute 'git status' in the project directory"
  - "Run a Python script"

### 3. Utility Skills

#### tavily_search Skill
**Activation Triggers:**
- Keywords: "latest", "recent", "current", "today", "now", "news", "update", "weather", "temperature", "stock", "price"
- Time-sensitive queries: "what is", "when is", "where is", "how many", "statistics", "data", "facts", "research"
- Current information: Queries asking for up-to-date information, news, or real-time data
- Examples:
  - "What are the latest developments in AI?"
  - "What's the current weather in New York?"
  - "Find recent news about climate change"
  - "What's the stock price of Apple?"

#### route_skill Skill
**Activation Triggers:**
- This skill is automatically activated for all user queries
- It analyzes the query and determines which other skill (if any) should be executed
- Provides intelligent routing based on LLM analysis rather than simple keyword matching

### 4. Routing Priority and Logic

1. **Primary Routing**: route_skill analyzes the query using LLM to determine the best skill
2. **Fallback Routing**: If route_skill fails, keyword-based fallback analysis is used
3. **Path Pattern Recognition**: File paths in queries strongly indicate file system operations
4. **Command Pattern Recognition**: Shell command patterns indicate execute_command skill
5. **Context Awareness**: Conversation history is considered for better decision making
6. **Confidence Scoring**: Each skill selection includes a confidence score (0.0 to 1.0)

### 5. Decision Flow

```
User Query
    ↓
route_skill Analysis (LLM-based)
    ↓
High Confidence Match? → Execute Selected Skill
    ↓
Low Confidence / No Match
    ↓
Keyword-based Fallback Analysis
    ↓
Execute Best Match Skill or Direct Response
```

### 6. Special Cases

- **File Path Detection**: Queries containing paths like "/home/user/file.txt" or "~/documents" are prioritized for file system skills
- **Command Detection**: Queries with command-like patterns trigger execute_command skill
- **Time-sensitive Detection**: Queries with time-related keywords trigger tavily_search skill
- **Multi-skill Queries**: Complex queries may require multiple skills executed in sequence

## Security Considerations

- All file operations should validate paths to prevent directory traversal
- Shell commands should be carefully validated and sandboxed where possible
- Sensitive operations should require explicit user confirmation
- Log all skill executions for audit purposes
- Path validation prevents access outside current working directory
- Command execution has built-in security checks and timeouts
- File content validation prevents writing potentially dangerous content
