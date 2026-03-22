import subprocess
import os
import shlex
import signal
import time
from typing import Dict, Any
from pathlib import Path


def execute_command(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes shell commands on the local system and returns the output.
    
    Args:
        parameters: Dictionary containing:
            - command (str): The shell command to execute
            - timeout (int, optional): Maximum execution time in milliseconds (default: 30000)
            - capture_output (bool, optional): Whether to capture command output (default: True)
            - shell (bool, optional): Whether to execute through shell (default: True)
            - working_dir (str, optional): Working directory for the command (default: current directory)
    
    Returns:
        Dictionary containing:
            - success (bool): Whether the command executed successfully
            - stdout (str): Standard output from the command
            - stderr (str): Standard error output from the command
            - return_code (int): Command exit code
            - execution_time (float): Time taken to execute in seconds
            - message (str): Human-readable status message
    """
    try:
        # Extract parameters with defaults
        command = parameters.get('command', '')
        timeout = parameters.get('timeout', 30000)
        capture_output = parameters.get('capture_output', True)
        shell = parameters.get('shell', True)
        working_dir = parameters.get('working_dir', None)
        
        # Validate required parameters
        if not command:
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "return_code": -1,
                "execution_time": 0,
                "message": "No command provided"
            }
        
        # Security validation - block dangerous commands
        dangerous_commands = [
            'rm -rf /', 'rm -rf /*', 'rm -rf *', 'sudo rm',
            'dd if=', 'mkfs.', 'fdisk', 'format',
            'shutdown', 'reboot', 'poweroff', 'halt',
            'chmod 777', 'chmod 666', 'chown root',
            'passwd', 'useradd', 'userdel', 'usermod',
            'mount', 'umount', 'fsck', 'mkfs',
            'iptables -F', 'iptables --flush',
            'netstat -tulnp', 'ss -tulnp', 'lsof -i',
            'cat /etc/passwd', 'cat /etc/shadow', 'cat /etc/sudoers',
            'find / -name', 'find / -type f', 'find / -exec',
            'grep -r', 'grep -R', 'rgrep',
            'wget', 'curl', 'scp', 'rsync', 'nc', 'netcat',
            'python -c', 'python3 -c', 'perl -e', 'ruby -e', 'php -r',
            'eval', 'exec', 'source', 'bash -c', 'sh -c'
        ]
        
        # Convert command to lowercase for case-insensitive comparison
        command_lower = command.lower().strip()
        
        # Check for exact matches of dangerous commands
        for dangerous_cmd in dangerous_commands:
            if command_lower.startswith(dangerous_cmd):
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "",
                    "return_code": -1,
                    "execution_time": 0,
                    "message": f"Command blocked for security: '{command}'"
                }
        
        # Additional pattern checks
        import re
        
        # Check for rm commands with wildcards
        if re.match(r'^\s*rm\s+.*[\*\?]', command_lower):
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "return_code": -1,
                "execution_time": 0,
                "message": f"Command blocked for security: Dangerous rm command with wildcards"
            }
        
        # Check for sudo commands
        if command_lower.startswith('sudo '):
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "return_code": -1,
                "execution_time": 0,
                "message": f"Command blocked for security: Sudo commands are not allowed"
            }
        
        # Check for file system modification commands
        filesystem_mod_commands = ['mkfs', 'fdisk', 'parted', 'mount', 'umount', 'fsck']
        for cmd in filesystem_mod_commands:
            if command_lower.startswith(cmd):
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "",
                    "return_code": -1,
                    "execution_time": 0,
                    "message": f"Command blocked for security: Filesystem modification commands are not allowed"
                }
        
        # Validate working directory
        if working_dir:
            try:
                working_path = Path(working_dir).resolve()
                current_working_dir = Path.cwd().resolve()
                
                # Security check: ensure working directory is within current working directory
                working_path.relative_to(current_working_dir)
            except ValueError:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "",
                    "return_code": -1,
                    "execution_time": 0,
                    "message": f"Access denied: Working directory '{working_dir}' is outside the allowed directory scope"
                }
        else:
            working_dir = str(Path.cwd())
        
        # Convert timeout from milliseconds to seconds
        timeout_seconds = timeout / 1000.0
        
        # Prepare command execution
        start_time = time.time()
        
        try:
            # Execute the command
            if shell:
                # Use shell=True for complex commands
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE if capture_output else None,
                    text=True,
                    cwd=working_dir,
                    env=os.environ.copy()
                )
            else:
                # Use shell=False for safer execution
                cmd_args = shlex.split(command)
                process = subprocess.Popen(
                    cmd_args,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE if capture_output else None,
                    text=True,
                    cwd=working_dir,
                    env=os.environ.copy()
                )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                # Kill the process if it times out
                process.kill()
                stdout, stderr = process.communicate()
                return_code = -1
                
                return {
                    "success": False,
                    "stdout": stdout if stdout else "",
                    "stderr": stderr if stderr else "",
                    "return_code": return_code,
                    "execution_time": timeout_seconds,
                    "message": f"Command timed out after {timeout_seconds} seconds"
                }
            
            execution_time = time.time() - start_time
            
            # Determine success based on return code
            success = return_code == 0
            
            if success:
                message = f"Command executed successfully in {execution_time:.2f} seconds"
            else:
                message = f"Command failed with return code {return_code} after {execution_time:.2f} seconds"
            
            return {
                "success": success,
                "stdout": stdout if stdout else "",
                "stderr": stderr if stderr else "",
                "return_code": return_code,
                "execution_time": execution_time,
                "message": message
            }
            
        except FileNotFoundError:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command not found: {command}",
                "return_code": -1,
                "execution_time": 0,
                "message": f"Command not found: {command}"
            }
            
        except PermissionError:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Permission denied: {command}",
                "return_code": -1,
                "execution_time": 0,
                "message": f"Permission denied: {command}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
                "message": f"Error executing command: {str(e)}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "return_code": -1,
            "execution_time": 0,
            "message": f"Error executing command: {str(e)}"
        }