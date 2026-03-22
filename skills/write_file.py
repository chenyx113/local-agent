import os
from typing import Dict, Any
from pathlib import Path
import re


def write_file(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Writes content to a specified file, creating the file if it doesn't exist or overwriting it if it does.
    
    Args:
        parameters: Dictionary containing:
            - path (str): The file path to write to
            - content (str): The content to write to the file
            - encoding (str, optional): File encoding (default: 'utf-8')
            - mode (str, optional): Write mode ('overwrite' or 'append', default: 'overwrite')
            - create_dirs (bool, optional): Whether to create parent directories if they don't exist (default: True)
    
    Returns:
        Dictionary containing:
            - success (bool): Whether the operation was successful
            - file_path (str): The absolute path of the written file
            - file_size (int): Size of the written content in bytes
            - message (str): Human-readable status message
    """
    try:
        # Get current working directory for security validation
        current_working_dir = Path.cwd().resolve()
        
        # Extract parameters with defaults
        path = parameters.get('path', '')
        content = parameters.get('content', '')
        encoding = parameters.get('encoding', 'utf-8')
        mode = parameters.get('mode', 'overwrite').lower()
        create_dirs = parameters.get('create_dirs', True)
        
        # Validate required parameters
        if not path:
            return {
                "success": False,
                "file_path": "",
                "file_size": 0,
                "message": "No file path provided"
            }
        
        if content is None:
            return {
                "success": False,
                "file_path": "",
                "file_size": 0,
                "message": "No content provided"
            }
        
        # Validate mode parameter
        if mode not in ['overwrite', 'append']:
            return {
                "success": False,
                "file_path": "",
                "file_size": 0,
                "message": "Invalid mode. Must be 'overwrite' or 'append'"
            }
        
        # Validate and resolve path
        target_path = Path(path).resolve()
        
        # Security check: ensure path is within current working directory
        try:
            target_path.relative_to(current_working_dir)
        except ValueError:
            return {
                "success": False,
                "file_path": "",
                "file_size": 0,
                "message": f"Access denied: Path '{path}' is outside the allowed directory scope"
            }
        
        # Safety checks for critical system files
        critical_paths = [
            '/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin', '/boot', '/dev', '/proc', '/sys',
            '/var/log', '/var/run', '/var/spool', '/var/tmp', '/tmp'
        ]
        
        # Convert to string for comparison
        target_path_str = str(target_path)
        for critical_path in critical_paths:
            if target_path_str.startswith(critical_path):
                return {
                    "success": False,
                    "file_path": "",
                    "file_size": 0,
                    "message": f"Access denied: Cannot write to system directory '{target_path_str}'"
                }
        
        # Check if parent directory exists or can be created
        parent_dir = target_path.parent
        
        if not parent_dir.exists():
            if create_dirs:
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    return {
                        "success": False,
                        "file_path": "",
                        "file_size": 0,
                        "message": f"Permission denied: Cannot create directory '{parent_dir}'"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "file_path": "",
                        "file_size": 0,
                        "message": f"Error creating directory: {str(e)}"
                    }
            else:
                return {
                    "success": False,
                    "file_path": "",
                    "file_size": 0,
                    "message": f"Parent directory '{parent_dir}' does not exist and create_dirs is False"
                }
        
        # Validate file content (basic safety check)
        if not isinstance(content, str):
            content = str(content)
        
        # Check for potentially dangerous content patterns
        dangerous_patterns = [
            r'rm\s+-rf',  # Dangerous shell commands
            r'chmod\s+777',  # Overly permissive permissions
            r'eval\s*\(',  # Code evaluation
            r'exec\s*\(',  # Code execution
            r'import\s+os\s*\n\s*os\.system',  # System command execution
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    "success": False,
                    "file_path": "",
                    "file_size": 0,
                    "message": "Content validation failed: Potentially dangerous content detected"
                }
        
        # Write the file
        try:
            file_mode = 'a' if mode == 'append' else 'w'
            
            with open(target_path, file_mode, encoding=encoding) as file:
                file.write(content)
            
            # Get file size
            file_size = len(content.encode(encoding))
            
            return {
                "success": True,
                "file_path": str(target_path),
                "file_size": file_size,
                "message": f"Successfully wrote {file_size} bytes to '{path}'"
            }
            
        except PermissionError:
            return {
                "success": False,
                "file_path": "",
                "file_size": 0,
                "message": f"Permission denied: Cannot write to '{path}'"
            }
            
        except UnicodeEncodeError as e:
            return {
                "success": False,
                "file_path": "",
                "file_size": 0,
                "message": f"Encoding error: {str(e)}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "file_path": "",
                "file_size": 0,
                "message": f"Error writing file: {str(e)}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "file_path": "",
            "file_size": 0,
            "message": f"Error writing file: {str(e)}"
        }