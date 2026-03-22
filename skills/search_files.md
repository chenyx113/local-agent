# Search Files Skill

## Description
Searches for files and content using regex patterns within a specified directory.

## Purpose
This skill allows the AI assistant to search for files and content patterns in the local file system. It's useful for:
- Finding files by name patterns
- Searching for specific content within files
- Code analysis and refactoring
- Log analysis
- Configuration file discovery
- Documentation search

## Input Parameters
- **path** (string): The directory path to search in
- **pattern** (string): The regex pattern to search for
- **file_pattern** (string, optional): Glob pattern to filter files (default: '*')
- **recursive** (boolean, optional): Whether to search recursively (default: true)
- **max_results** (integer, optional): Maximum number of results to return (default: 100)
- **context_lines** (integer, optional): Number of context lines to include around matches (default: 2)

## Output
Returns a dictionary containing:
- **success** (boolean): Whether the search was successful
- **results** (list): List of search results, each containing:
  - **file_path** (string): Path to the matching file
  - **line_number** (integer): Line number where match was found
  - **content** (string): The matching content
  - **context** (string): Context around the match (if requested)
- **total_matches** (integer): Total number of matches found
- **total_files_searched** (integer): Total number of files searched
- **message** (string): Human-readable status message

## Examples
```
User: "Find all Python files in the project"
Assistant: Uses search_files skill with path="." and file_pattern="*.py"

User: "Search for TODO comments in the codebase"
Assistant: Uses search_files skill with path="." and pattern="TODO|FIXME|XXX"

User: "Find all function definitions in JavaScript files"
Assistant: Uses search_files skill with path="." and pattern="function\s+\w+" and file_pattern="*.js"

User: "Search for error messages in log files"
Assistant: Uses search_files skill with path="logs/" and pattern="ERROR|Exception" and file_pattern="*.log"
```

## Implementation Notes
- Uses Python's re module for regex pattern matching
- Supports both file name filtering and content search
- Recursive search is enabled by default but can be limited
- Results include context lines for better understanding
- Performance optimized for large codebases
- Security validation prevents directory traversal
- Results are sorted by modification time