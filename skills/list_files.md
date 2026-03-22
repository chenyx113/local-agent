# List Files Skill

## Description
Lists files and directories in a specified path.

## Purpose
This skill allows the AI assistant to explore the file system and provide information about the contents of directories. It's useful for:
- Finding specific files or directories
- Understanding project structure
- Locating configuration files
- Exploring available resources

## Input Parameters
- **path** (string): The directory path to list files from
- **recursive** (boolean, optional): Whether to list files recursively (default: false)
- **include_hidden** (boolean, optional): Whether to include hidden files (starting with dot) (default: false)

## Output
Returns a dictionary containing:
- **success** (boolean): Whether the operation was successful
- **files** (list): List of file/directory names
- **directories** (list): List of directory names
- **total_count** (integer): Total number of items found
- **message** (string): Human-readable status message

## Examples
```
User: "List files in the current directory"
Assistant: Uses list_files skill with path="."

User: "Show me all files in the project directory recursively"
Assistant: Uses list_files skill with path="/home/user/project" and recursive=true

User: "What hidden files are in the home directory?"
Assistant: Uses list_files skill with path="/home/user" and include_hidden=true
```

## Implementation Notes
- Path validation is performed to prevent directory traversal attacks
- Only allows access to files within the current working directory and its subdirectories
- Hidden files are excluded by default for security reasons
- Recursive listing is limited to prevent excessive resource usage
- Returns structured data that can be easily processed by the AI