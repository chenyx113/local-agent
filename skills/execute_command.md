# Execute Command Skill

## Description
Executes shell commands on the local system and returns the output.

## Purpose
This skill allows the AI assistant to execute system commands and retrieve their output. It's useful for:
- Running system diagnostics
- Managing files and directories
- Installing packages
- Checking system status
- Automating system tasks
- Running development tools

## Input Parameters
- **command** (string): The shell command to execute
- **timeout** (integer, optional): Maximum execution time in milliseconds (default: 30000ms / 30 seconds)
- **capture_output** (boolean, optional): Whether to capture command output (default: true)
- **shell** (boolean, optional): Whether to execute through shell (default: true)
- **working_dir** (string, optional): Working directory for the command (default: current directory)

## Output
Returns a dictionary containing:
- **success** (boolean): Whether the command executed successfully
- **stdout** (string): Standard output from the command
- **stderr** (string): Standard error output from the command
- **return_code** (integer): Command exit code
- **execution_time** (float): Time taken to execute in seconds
- **message** (string): Human-readable status message

## Examples
```
User: "Check the current directory"
Assistant: Uses execute_command skill with command="pwd"

User: "List files in the current directory"
Assistant: Uses execute_command skill with command="ls -la"

User: "Check system memory usage"
Assistant: Uses execute_command skill with command="free -h"

User: "Run a Python script"
Assistant: Uses execute_command skill with command="python script.py"
```

## Implementation Notes
- Commands are executed with limited privileges for security
- Output is captured and returned to the AI
- Commands have a timeout to prevent hanging
- Shell injection protection is implemented
- Only safe, read-only commands are recommended
- Sensitive system commands may be restricted
- Command history is logged for security auditing