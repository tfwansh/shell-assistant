import subprocess
import re
import os
import platform
from user_info import is_in_home_directory

def filter_unnecessary_sudo(command):
    """Filter out unnecessary sudo usage based on platform"""
    system = platform.system()
    
    # List of commands that typically don't need sudo
    user_space_commands = ['ls', 'cd', 'mkdir', 'touch', 'rm', 'cp', 'mv', 'cat', 'echo', 
                          'grep', 'find', 'pwd', 'less', 'more', 'head', 'tail', 'nano', 
                          'vim', 'tar', 'zip', 'unzip', 'python', 'node', 'npm']
    
    # Add macOS-specific commands
    if system == "Darwin":
        user_space_commands.extend(['open', 'defaults', 'say', 'afplay', 'screencapture'])
    
    # If command starts with sudo
    if command.strip().startswith('sudo'):
        for c in user_space_commands:
            if re.match(rf'sudo\s+{c}\b', command):
                return re.sub(r'^sudo\s+', '', command)
    return command


def is_safe_command(command):
    """Check if command is safe to execute based on platform"""
    system = platform.system()
    
    # Platform-specific dangerous patterns
    if system == "Darwin":  # macOS
        dangerous_patterns = [
            r'rm\s+-rf\s+/', 
            r'sudo\s+rm', 
            r'mkfs',
            r'dd\s+if=',
            r'passwd',
            r'chmod\s+777',
            r'>\s+/System',
            r'>\s+/Library',
            r'>\s+/Applications',
            r'sudo\s+rm\s+-rf\s+/',
            r'diskutil\s+eraseDisk',
            r'fdisk',
            r'format'
        ]
    else:  # Linux
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
    
    # Check if command exists on macOS and suggest Homebrew if missing
    if system == "Darwin":
        cmd = command.split()[0]
        preferred_cmd = get_preferred_command(cmd)
        if not command_exists(preferred_cmd):
            return False  # Not safe if command doesn't exist
    
    return True

def execute_command(command, user_info):
    """Execute command with platform-specific considerations"""
    if not is_safe_command(command):
        return "This command requires authentication or is not safe to execute."
    
    try:
        # Change to user's home directory before executing
        os.chdir(user_info['home'])
        
        # Set environment variables for better compatibility
        env = os.environ.copy()
        env['HOME'] = user_info['home']
        env['USER'] = user_info['username']
        
        # Execute the command and capture output
        result = subprocess.run(command, shell=True, 
                                capture_output=True, 
                                text=True,
                                env=env)
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except Exception as e:
        return f"Error executing command: {str(e)}"

def command_exists(cmd):
    """Check if a command exists in $PATH"""
    return subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def get_preferred_command(cmd):
    """On macOS, prefer GNU/coreutils if available (e.g., gls for ls)"""
    system = platform.system()
    if system == "Darwin":
        gnu_cmd = f"g{cmd}"
        if command_exists(gnu_cmd):
            return gnu_cmd
    return cmd

