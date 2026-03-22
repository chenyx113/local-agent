import os
import re
import glob
from typing import Dict, Any, List
from pathlib import Path


def search_files(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Searches for files and content using regex patterns within a specified directory.
    
    Args:
        parameters: Dictionary containing:
            - path (str): The directory path to search in
            - pattern (str): The regex pattern to search for
            - file_pattern (str, optional): Glob pattern to filter files (default: '*')
            - recursive (bool, optional): Whether to search recursively (default: True)
            - max_results (int, optional): Maximum number of results to return (default: 100)
            - context_lines (int, optional): Number of context lines to include around matches (default: 2)
    
    Returns:
        Dictionary containing:
            - success (bool): Whether the search was successful
            - results (list): List of search results
            - total_matches (int): Total number of matches found
            - total_files_searched (int): Total number of files searched
            - message (str): Human-readable status message
    """
    try:
        # Get current working directory for security validation
        current_working_dir = Path.cwd().resolve()
        
        # Extract parameters with defaults
        path = parameters.get('path', '.')
        pattern = parameters.get('pattern', '')
        file_pattern = parameters.get('file_pattern', '*')
        recursive = parameters.get('recursive', True)
        max_results = parameters.get('max_results', 100)
        context_lines = parameters.get('context_lines', 2)
        
        # Validate required parameters
        if not path:
            return {
                "success": False,
                "results": [],
                "total_matches": 0,
                "total_files_searched": 0,
                "message": "No search path provided"
            }
        
        if not pattern:
            return {
                "success": False,
                "results": [],
                "total_matches": 0,
                "total_files_searched": 0,
                "message": "No search pattern provided"
            }
        
        # Validate and resolve path
        target_path = Path(path).resolve()
        
        # Security check: ensure path is within current working directory
        try:
            target_path.relative_to(current_working_dir)
        except ValueError:
            return {
                "success": False,
                "results": [],
                "total_matches": 0,
                "total_files_searched": 0,
                "message": f"Access denied: Path '{path}' is outside the allowed directory scope"
            }
        
        # Check if path exists and is a directory
        if not target_path.exists():
            return {
                "success": False,
                "results": [],
                "total_matches": 0,
                "total_files_searched": 0,
                "message": f"Path '{path}' does not exist"
            }
        
        if not target_path.is_dir():
            return {
                "success": False,
                "results": [],
                "total_matches": 0,
                "total_files_searched": 0,
                "message": f"Path '{path}' is not a directory"
            }
        
        # Compile regex pattern
        try:
            regex_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            return {
                "success": False,
                "results": [],
                "total_matches": 0,
                "total_files_searched": 0,
                "message": f"Invalid regex pattern: {str(e)}"
            }
        
        # Prepare file search
        results = []
        total_files_searched = 0
        total_matches = 0
        
        # Build glob pattern
        if recursive:
            glob_pattern = f"{target_path}/**/{file_pattern}"
        else:
            glob_pattern = f"{target_path}/{file_pattern}"
        
        try:
            # Find all matching files
            files_to_search = glob.glob(glob_pattern, recursive=recursive)
            
            # Filter out directories and keep only files
            files_to_search = [f for f in files_to_search if Path(f).is_file()]
            
            total_files_searched = len(files_to_search)
            
            # Search each file
            for file_path in files_to_search:
                if len(results) >= max_results:
                    break
                
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        lines = file.readlines()
                    
                    # Search for pattern in each line
                    for line_num, line in enumerate(lines, 1):
                        if len(results) >= max_results:
                            break
                        
                        matches = list(regex_pattern.finditer(line))
                        
                        for match in matches:
                            total_matches += 1
                            
                            # Get context if requested
                            context = ""
                            if context_lines > 0:
                                start_line = max(0, line_num - context_lines - 1)
                                end_line = min(len(lines), line_num + context_lines)
                                
                                context_lines_list = []
                                for i in range(start_line, end_line):
                                    line_prefix = ">>>" if i == line_num - 1 else "   "
                                    context_lines_list.append(f"{line_prefix} {i+1:4d}: {lines[i].rstrip()}")
                                
                                context = "\n".join(context_lines_list)
                            
                            # Create result entry
                            result_entry = {
                                "file_path": str(Path(file_path).relative_to(current_working_dir)),
                                "line_number": line_num,
                                "content": line.rstrip(),
                                "match": match.group(),
                                "context": context
                            }
                            
                            results.append(result_entry)
                            
                except PermissionError:
                    # Skip files we don't have permission to read
                    continue
                except Exception as e:
                    # Skip files that can't be read
                    continue
            
            # Sort results by modification time (newest first)
            def get_mod_time(result):
                try:
                    return Path(result["file_path"]).stat().st_mtime
                except:
                    return 0
            
            results.sort(key=get_mod_time, reverse=True)
            
            success = True
            message = f"Search completed: {total_matches} matches found in {total_files_searched} files"
            
        except Exception as e:
            return {
                "success": False,
                "results": [],
                "total_matches": 0,
                "total_files_searched": 0,
                "message": f"Error during search: {str(e)}"
            }
        
        return {
            "success": success,
            "results": results,
            "total_matches": total_matches,
            "total_files_searched": total_files_searched,
            "message": message
        }
        
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "total_matches": 0,
            "total_files_searched": 0,
            "message": f"Error searching files: {str(e)}"
        }