# Write File Skill

## Description
Writes content to a specified file, creating the file if it doesn't exist or overwriting it if it does.

## Purpose
This skill allows the AI assistant to create and modify files on the local file system. It's useful for:
- Creating new files and documents
- Updating configuration files
- Writing code files
- Saving data and logs
- Generating reports and documentation

## Input Parameters
- **path** (string): The file path to write to
- **content** (string): The content to write to the file
- **encoding** (string, optional): File encoding (default: 'utf-8')
- **mode** (string, optional): Write mode ('overwrite' or 'append', default: 'overwrite')
- **create_dirs** (boolean, optional): Whether to create parent directories if they don't exist (default: true)

## Output
Returns a dictionary containing:
- **success** (boolean): Whether the operation was successful
- **file_path** (string): The absolute path of the written file
- **file_size** (integer): Size of the written content in bytes
- **message** (string): Human-readable status message

## Examples
```
User: "Create a new file called notes.txt with some content"
Assistant: Uses write_file skill with path="notes.txt" and content="Your notes here..."

User: "Add a new line to the existing log file"
Assistant: Uses write_file skill with path="app.log", content="New log entry\n", and mode="append"

User: "Save this configuration to config.json"
Assistant: Uses write_file skill with path="config.json" and the configuration content
```

## Implementation Notes
- Path validation is performed to prevent directory traversal attacks
- Only allows writing to files within the current working directory and its subdirectories
- Supports both overwrite and append modes
- Can automatically create parent directories
- Validates file content to prevent writing potentially harmful content
- Returns detailed information about the operation
- Includes safety checks to prevent overwriting critical system files