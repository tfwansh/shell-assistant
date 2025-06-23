import ollama
from pydantic import BaseModel, Field
import json
import platform

class CommandOutput(BaseModel):
    """Schema for structured command output"""
    command: str = Field(description="The exact shell command to execute without any conversational text")
    requires_sudo: bool = Field(default=False, description="Whether this command requires sudo privileges")
    notes: str = Field(default="", description="Optional notes about the command execution")

def interpret_command(user_input, distro_info, user_info):
    """
    Interpret natural language input and convert it to a shell command
    using structured output to ensure clean command responses.
    """
    system = platform.system()
    
    # Create platform-specific system prompt
    if system == "Darwin":  # macOS
        system_prompt = f"""You are a macOS command generator that converts natural language to precise shell commands.

System information:
{distro_info}

User information:
Username: {user_info['username']}
Home Directory: {user_info['home']}
Available user folders: {', '.join(user_info['folders'].keys())}

CRITICAL RULES FOR macOS COMMANDS:

1. ALWAYS prefer standard Unix/GNU utilities first:
   - File operations: ls, find, grep, cat, head, tail, less, more
   - Text processing: sed, awk, sort, uniq, wc, cut, tr
   - Compression: tar, gzip, bzip2, zip, unzip
   - Downloads: curl, wget
   - Text editing: vim, nano
   - System info: df, du, ps, top, who, date

2. ONLY use macOS-specific tools when absolutely necessary:
   - 'open' ONLY for: opening applications, launching URLs in browser, opening files with default apps
   - 'defaults' ONLY for: system preferences that can't be changed otherwise
   - 'brew' ONLY for: package installation/management
   - 'say', 'afplay', 'screencapture' ONLY when specifically requested

3. EXAMPLES of correct command choices:
   - "search for text": use 'grep -r "text" .' NOT 'open'
   - "compress folder": use 'tar -czf archive.tar.gz folder/' NOT 'open'
   - "download file": use 'curl -O url' NOT 'open'
   - "edit file": use 'vim file.txt' or 'nano file.txt' NOT 'open'
   - "check disk space": use 'df -h' NOT 'open'
   - "open website": use 'open https://example.com' (this is correct use of open)

4. NEVER use sudo unless absolutely necessary for system modifications.

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "command": "the exact shell command to execute",
  "requires_sudo": false,
  "notes": "brief explanation of what the command does"
}}

NO markdown, NO explanations, NO code blocks - ONLY the JSON object."""
    else:  # Linux
        system_prompt = f"""You are a Linux command generator that converts natural language to precise shell commands.

System information:
{distro_info}

User information:
Username: {user_info['username']}
Home Directory: {user_info['home']}
Available user folders: {', '.join(user_info['folders'].keys())}

IMPORTANT RULES FOR LINUX:
1. DO NOT use sudo for operations that don't require root privileges
2. Only mark requires_sudo as true when absolutely necessary (system modifications, package installs, etc.)
3. Use appropriate Linux commands and tools
4. Prefer user-space operations over system operations

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "command": "the exact shell command to execute",
  "requires_sudo": false,
  "notes": "optional explanation"
}}

NO markdown, NO explanations, NO code blocks - ONLY the JSON object."""

    try:
        # Get the schema for structured output
        schema = CommandOutput.model_json_schema()
        
        # Call Ollama with structured output
        response = ollama.chat(
            model='deepseek-coder',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input}
            ],
            format=schema
        )
        
        # Extract the content from the response
        if isinstance(response, dict) and 'message' in response:
            content = response['message']['content']
        else:
            # Fallback: try to get content directly
            content = response.get('content', response)
        
        # Parse the JSON content
        if isinstance(content, str):
            # Parse the JSON string
            parsed_content = json.loads(content)
        else:
            # Content is already a dict
            parsed_content = content
        
        # Validate with Pydantic
        command_output = CommandOutput(**parsed_content)
        
        return command_output
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Model did not return valid output: {e}")

