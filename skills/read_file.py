import os
from typing import Dict, Any
from pathlib import Path


def read_file(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads and returns the content of a specified file.
    
    Args:
        parameters: Dictionary containing:
            - path (str): The file path to read
            - encoding (str, optional): File encoding (default: 'utf-8')
            - max_lines (int, optional): Maximum number of lines to read (default: 1000)
            - offset (int, optional): Line number to start reading from (default: 0)
    
    Returns:
        Dictionary containing:
            - success (bool): Whether the operation was successful
            - content (str): The file content (or partial content if limited)
            - total_lines (int): Total number of lines in the file
            - read_lines (int): Number of lines actually read
            - file_size (int): File size in bytes
            - message (str): Human-readable status message
    """
    try:
        # Get current working directory for security validation
        current_working_dir = Path.cwd().resolve()
        
        # Extract parameters with defaults
        path = parameters.get('path', '')
        encoding = parameters.get('encoding', 'utf-8')
        max_lines = parameters.get('max_lines', 1000)
        offset = parameters.get('offset', 0)
        
        # Validate path parameter
        if not path:
            return {
                "success": False,
                "content": "",
                "total_lines": 0,
                "read_lines": 0,
                "file_size": 0,
                "message": "No file path provided"
            }
        
        # Validate and resolve path
        target_path = Path(path).resolve()
        
        # Security check: ensure path is within current working directory
        try:
            target_path.relative_to(current_working_dir)
        except ValueError:
            return {
                "success": False,
                "content": "",
                "total_lines": 0,
                "read_lines": 0,
                "file_size": 0,
                "message": f"Access denied: Path '{path}' is outside the allowed directory scope"
            }
        
        # Check if path exists and is a file
        if not target_path.exists():
            return {
                "success": False,
                "content": "",
                "total_lines": 0,
                "read_lines": 0,
                "file_size": 0,
                "message": f"File '{path}' does not exist"
            }
        
        if not target_path.is_file():
            return {
                "success": False,
                "content": "",
                "total_lines": 0,
                "read_lines": 0,
                "file_size": 0,
                "message": f"Path '{path}' is not a file"
            }
        
        # Get file size
        file_size = target_path.stat().st_size
        
        # Read file content
        try:
            with open(target_path, 'r', encoding=encoding) as file:
                lines = file.readlines()
                
                total_lines = len(lines)
                
                # Apply offset and limit
                if offset < 0:
                    offset = 0
                if offset >= total_lines:
                    offset = total_lines - 1 if total_lines > 0 else 0
                
                if max_lines < 0:
                    max_lines = 1000
                
                end_line = min(offset + max_lines, total_lines)
                read_lines = end_line - offset
                
                # Extract content
                content_lines = lines[offset:end_line]
                content = ''.join(content_lines)
                
                return {
                    "success": True,
                    "content": content,
                    "total_lines": total_lines,
                    "read_lines": read_lines,
                    "file_size": file_size,
                    "message": f"Successfully read {read_lines} lines from '{path}'"
                }
                
        except UnicodeDecodeError:
            # Try different encodings for text files
            encodings_to_try = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for enc in encodings_to_try:
                try:
                    with open(target_path, 'r', encoding=enc) as file:
                        lines = file.readlines()
                        total_lines = len(lines)
                        
                        if offset < 0:
                            offset = 0
                        if offset >= total_lines:
                            offset = total_lines - 1 if total_lines > 0 else 0
                        
                        if max_lines < 0:
                            max_lines = 1000
                        
                        end_line = min(offset + max_lines, total_lines)
                        read_lines = end_line - offset
                        
                        content_lines = lines[offset:end_line]
                        content = ''.join(content_lines)
                        
                        return {
                            "success": True,
                            "content": content,
                            "total_lines": total_lines,
                            "read_lines": read_lines,
                            "file_size": file_size,
                            "message": f"Successfully read {read_lines} lines from '{path}' using {enc} encoding"
                        }
                        
                except UnicodeDecodeError:
                    continue
            
            # If all text encodings fail, it might be a binary file
            return {
                "success": False,
                "content": "",
                "total_lines": 0,
                "read_lines": 0,
                "file_size": file_size,
                "message": f"File '{path}' appears to be a binary file or uses an unsupported encoding"
            }
            
        except PermissionError:
            return {
                "success": False,
                "content": "",
                "total_lines": 0,
                "read_lines": 0,
                "file_size": file_size,
                "message": f"Permission denied: Cannot read '{path}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "total_lines": 0,
                "read_lines": 0,
                "file_size": file_size,
                "message": f"Error reading file: {str(e)}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "content": "",
            "total_lines": 0,
            "read_lines": 0,
            "file_size": 0,
            "message": f"Error reading file: {str(e)}"
        }