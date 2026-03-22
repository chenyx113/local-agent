import os
from typing import Dict, Any, List
from pathlib import Path


def list_files(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lists files and directories in a specified path.
    
    Args:
        parameters: Dictionary containing:
            - path (str): The directory path to list files from
            - recursive (bool, optional): Whether to list files recursively (default: False)
            - include_hidden (bool, optional): Whether to include hidden files (default: False)
    
    Returns:
        Dictionary containing:
            - success (bool): Whether the operation was successful
            - files (list): List of file/directory names
            - directories (list): List of directory names
            - total_count (int): Total number of items found
            - message (str): Human-readable status message
    """
    try:
        # Get current working directory for security validation
        current_working_dir = Path.cwd().resolve()
        
        # Extract parameters with defaults
        path = parameters.get('path', '.')
        recursive = parameters.get('recursive', False)
        include_hidden = parameters.get('include_hidden', False)
        
        # Validate and resolve path
        target_path = Path(path).resolve()
        
        # Security check: ensure path is within current working directory
        try:
            target_path.relative_to(current_working_dir)
        except ValueError:
            return {
                "success": False,
                "files": [],
                "directories": [],
                "total_count": 0,
                "message": f"Access denied: Path '{path}' is outside the allowed directory scope"
            }
        
        # Check if path exists and is a directory
        if not target_path.exists():
            return {
                "success": False,
                "files": [],
                "directories": [],
                "total_count": 0,
                "message": f"Path '{path}' does not exist"
            }
        
        if not target_path.is_dir():
            return {
                "success": False,
                "files": [],
                "directories": [],
                "total_count": 0,
                "message": f"Path '{path}' is not a directory"
            }
        
        # List files and directories
        files = []
        directories = []
        
        if recursive:
            # Recursive listing with depth limit to prevent excessive resource usage
            max_depth = 5  # Limit recursion depth
            
            def _list_recursive(current_path: Path, current_depth: int = 0):
                if current_depth >= max_depth:
                    return
                
                try:
                    for item in current_path.iterdir():
                        # Skip hidden files unless explicitly requested
                        if not include_hidden and item.name.startswith('.'):
                            continue
                        
                        if item.is_file():
                            files.append(str(item.relative_to(current_working_dir)))
                        elif item.is_dir():
                            directories.append(str(item.relative_to(current_working_dir)))
                            _list_recursive(item, current_depth + 1)
                except PermissionError:
                    # Skip directories we don't have permission to access
                    pass
            
            _list_recursive(target_path)
        else:
            # Non-recursive listing
            try:
                for item in target_path.iterdir():
                    # Skip hidden files unless explicitly requested
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    if item.is_file():
                        files.append(item.name)
                    elif item.is_dir():
                        directories.append(item.name)
            except PermissionError:
                return {
                    "success": False,
                    "files": [],
                    "directories": [],
                    "total_count": 0,
                    "message": f"Permission denied: Cannot access '{path}'"
                }
        
        # Sort the results for better readability
        files.sort()
        directories.sort()
        
        total_count = len(files) + len(directories)
        
        return {
            "success": True,
            "files": files,
            "directories": directories,
            "total_count": total_count,
            "message": f"Successfully listed {total_count} items from '{path}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "files": [],
            "directories": [],
            "total_count": 0,
            "message": f"Error listing files: {str(e)}"
        }