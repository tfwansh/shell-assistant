import ollama
from pydantic import BaseModel, Field
import json

class CommandOutput(BaseModel):
    """Schema for structured command output"""
    command: str = Field(description="The exact Linux command to execute without any conversational text")
    requires_sudo: bool = Field(default=False, description="Whether this command requires sudo privileges")
    notes: str = Field(default="", description="Optional notes about the command execution")

def interpret_command(user_input, distro_info, user_info):
    """
    Interpret natural language input and convert it to a Linux command
    using structured output to ensure clean command responses.
    """
    # Create a detailed system prompt with all the rules
    system_prompt = f"""You are a Linux command generator that converts natural language to precise shell commands.

Distribution information:
{distro_info}

User information:
Username: {user_info['username']}
Home Directory: {user_info['home']}
Available user folders: {', '.join(user_info['folders'].keys())}

IMPORTANT RULES:
1. DO NOT use sudo for operations that don't require root privileges
2. Only mark requires_sudo as true when absolutely necessary (system updates, service management, etc.)
3. For file operations within the user's home directory, NEVER use sudo
4. Always use the user's home directory as the base for file operations
5. Provide ONLY the exact command to execute - no explanations in the command field
6. If a command is potentially destructive, add appropriate notes
7. Always stay within the user's home directory unless explicitly requested otherwise
"""

    # Define the user prompt
    user_prompt = f"Convert this request into a Linux command: \"{user_input}\""

    try:
        # Use the json_schema method to get the schema
        schema = CommandOutput.model_json_schema()
        
        # Make the API call with structured output format
        response = ollama.chat(
            model='gemma:2b',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            format=schema
        )
        
        # Extract the content from the response
        content = response.message.content
        
        # Parse the JSON response
        try:
            # If the response is already a dict, use it directly
            if isinstance(content, dict):
                result = CommandOutput(**content)
            # Otherwise, parse the JSON string
            else:
                # Clean up the content if it contains markdown code blocks
          

             #   if "```json" in content:
             #       content = content.split("``````")[0]
             #   elif "```":
             #       content = content.split("```")[1]
                




                result = CommandOutput(**json.loads(content))
            
            # Return the command and any notes
            notes = result.notes
            if result.requires_sudo:
                if notes:
                    notes = f"This command requires sudo privileges. {notes}"
                else:
                    notes = "This command requires sudo privileges."
                    
            return result.command, notes
            
        except (json.JSONDecodeError, TypeError) as e:
            # Fallback for parsing errors - extract command using heuristics
            print(f"Error parsing structured output: {e}")
            print(f"Raw content: {content}")
            
            # Simple fallback parsing
            if isinstance(content, str):
                # Look for a command pattern
                lines = content.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#') and not line.lower().startswith(('sure', 'here', 'the command')):
                        return line.strip(), "Warning: Structured output failed, using best-guess command"
            
            return content.strip() if isinstance(content, str) else str(content), "Warning: Could not parse structured output"
            
    except Exception as e:
        print(f"Error in interpret_command: {str(e)}")
        return f"echo 'Error: {str(e)}'", "An error occurred while interpreting the command"

