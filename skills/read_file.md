# Read File Skill

## Description
Reads and returns the content of a specified file.

## Purpose
This skill allows the AI assistant to read files from the local file system. It's useful for:
- Reading configuration files
- Examining source code
- Reading documentation
- Analyzing data files
- Reviewing logs

## Input Parameters
- **path** (string): The file path to read
- **encoding** (string, optional): File encoding (default: 'utf-8')
- **max_lines** (integer, optional): Maximum number of lines to read (default: 1000)
- **offset** (integer, optional): Line number to start reading from (default: 0)

## Output
Returns a dictionary containing:
- **success** (boolean): Whether the operation was successful
- **content** (string): The file content (or partial content if limited)
- **total_lines** (integer): Total number of lines in the file
- **read_lines** (integer): Number of lines actually read
- **file_size** (integer): File size in bytes
- **message** (string): Human-readable status message

## Examples
```
User: "Read the content of config.json"
Assistant: Uses read_file skill with path="config.json"

User: "Show me the first 50 lines of main.py"
Assistant: Uses read_file skill with path="main.py" and max_lines=50

User: "Read lines 100-200 from the log file"
Assistant: Uses read_file skill with path="app.log", offset=100, max_lines=100
```

## Implementation Notes
- Path validation is performed to prevent directory traversal attacks
- Only allows access to files within the current working directory and its subdirectories
- Large files are handled by limiting the number of lines read
- Supports different file encodings
- Returns structured metadata about the file
- Text files are preferred; binary files may be handled differently