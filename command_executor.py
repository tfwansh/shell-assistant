import subprocess
import re
import os
from user_info import is_in_home_directory

def filter_unnecessary_sudo(command):
    # List of commands that typically don't need sudo
    user_space_commands = ['ls', 'cd', 'mkdir', 'touch', 'rm', 'cp', 'mv', 'cat', 'echo', 
                          'grep', 'find', 'pwd', 'less', 'more', 'head', 'tail', 'nano', 
                          'vim', 'tar', 'zip', 'unzip', 'python', 'node', 'npm']
    
    # If command starts with sudo
    if command.strip().startswith('sudo '):
        # Extract the actual command after sudo
        actual_command = command.strip()[5:].split()[0]
        
        # If it's a user space command, remove sudo
        if actual_command in user_space_commands:
            return command.replace('sudo ', '', 1)
    
    return command


def is_safe_command(command):
    # Existing dangerous patterns...
    dangerous_patterns = [
        r'rm\s+-rf\s+/', 
        r'sudo\s+rm', 
        r'mkfs',
        r'dd\s+if=',
        r'passwd',
        r'chmod\s+777',
        r'>\s+/etc',
        r'>\s+/boot'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            return False
    
    # Check if command tries to access outside home directory
    command_parts = command.split()
    for part in command_parts:
        if os.path.isabs(part) and not is_in_home_directory(part):
            return False
    
    return True

def execute_command(command, user_info):
    if not is_safe_command(command):
        return "This command requires authentication or is not safe to execute."
    
    try:
        # Change to user's home directory before executing
        os.chdir(user_info['home'])
        
        # Execute the command and capture output
        result = subprocess.run(command, shell=True, 
                                capture_output=True, 
                                text=True)
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except Exception as e:
        return f"Error executing command: {str(e)}"

