# Shell Assistant

A local application that interprets natural language commands and executes them on Linux and macOS systems. This tool uses Ollama to understand user intent and convert natural language into shell commands.

## Overview

Command Assistant provides a simple web interface that allows users to:
1. Enter commands in plain English
2. See the interpreted shell command before execution
3. Confirm execution with a yes/no prompt
4. View the command output

The application runs locally and interacts with a locally running Ollama model to interpret commands.

## Features

- Natural language command interpretation
- Command confirmation before execution
- Safety checks to prevent dangerous operations
- Platform-aware command generation (Linux and macOS)
- User-specific folder awareness
- Modern Catpuccin-themed UI
- Cross-platform compatibility

## Architecture

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Web Interface│     │  Flask Server │     │ Ollama Model  │
│   (Browser)   │───▶│  (Python)     │───▶│  (Local LLM)  │
└───────────────┘     └───────────────┘     └───────────────┘
                             │                      │
                             ▼                      ▼
                      ┌───────────────┐     ┌───────────────┐
                      │ Command       │     │ Command       │
                      │ Validation    │◀───│ Generation    │
                      └───────────────┘     └───────────────┘
                             │
                             ▼
                      ┌───────────────┐
                      │ Command       │
                      │ Execution     │
                      └───────────────┘
```

## Workflow

1. User enters a natural language command in the web interface
2. The request is sent to the Flask server
3. The server sends the request to the Ollama model along with system information
4. Ollama interprets the request and returns a shell command
5. The command is validated for safety
6. The user is prompted to confirm execution
7. If confirmed, the command is executed
8. Results are displayed to the user

## Prerequisites

- Python 3.6+
- Ollama installed locally
- A compatible Ollama model (e.g., gemma:2b)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/PSxUchiha/shell-assistantant.git
cd shell-assistantant
```

2. Install required Python packages:

```bash
pip install -r requirements.txt
```

3. Install and start Ollama:

**On macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

**On Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

4. Pull a compatible model:

```bash
ollama pull gemma:2b
```

## Project Structure

```
shell-assistant/
├── main.py                  # Main Flask application
├── distro_detector.py       # Platform detection module
├── command_executor.py      # Command execution module
├── ollama_interface.py      # Ollama API interface
├── user_info.py             # User information module
├── requirements.txt         # Python dependencies
└── templates/
    └── index.html           # Web interface template
```

## Running the Application

1. Start the application:

```bash
python main.py
```

2. For CLI mode (no web interface):

```bash
python main.py --cli
```

3. Open your browser and navigate to:

```
http://127.0.0.1:5000
```

## Usage Examples

Here are some examples of commands you can try:

**General commands:**
- "Show me all running processes"
- "Create a new folder called projects in my home directory"
- "List all files in my downloads folder"
- "Show system information"
- "Find all text files in my documents folder"

**macOS-specific commands:**
- "Take a screenshot"
- "Open the Applications folder"
- "Show me the contents of my Movies folder"
- "Set the volume to 50%"

**Linux-specific commands:**
- "Show me the contents of my Videos folder"
- "Check disk usage"

## Platform-Specific Features

### macOS Support
- Uses `sw_vers` and `system_profiler` for system information
- Recognizes macOS-specific folders (Movies, Public, Library)
- Supports macOS commands like `open`, `defaults`, `say`, `screencapture`
- Uses zsh-compatible syntax
- Includes macOS-specific safety patterns

### Linux Support
- Uses `lsb_release` and `/etc/os-release` for distribution detection
- Recognizes Linux folder structure
- Supports standard Linux commands
- Uses bash-compatible syntax
- Includes Linux-specific safety patterns

## Safety Considerations

The application includes several safety measures:

1. Commands are checked against a platform-specific blacklist of dangerous operations
2. Operations outside the user's home directory are restricted
3. Commands require confirmation before execution
4. System-wide operations are flagged with warnings
5. Platform-specific dangerous patterns are detected

## Customization

You can customize the application by:

1. Modifying the prompt in ollama_interface.py
2. Adding additional safety checks in command_executor.py
3. Updating the UI theme in index.html
4. Adding new command patterns to the interpreter

## Troubleshooting

If you encounter issues:

1. Check that Ollama is running: `ollama serve`
2. Verify you've pulled the correct model: `ollama list`
3. Check the Flask server logs for errors
4. Ensure all required Python packages are installed
5. On macOS, ensure you have the necessary permissions for commands

## Limitations

- Command interpretation quality depends on the Ollama model used
- Some complex commands may not be interpreted correctly
- The application has limited error handling for edge cases
- Platform-specific commands may not work across different operating systems

## Future Improvements

- Add command history
- Implement better error handling
- Add support for more complex command sequences
- Improve command validation logic
- Add user preferences and customization options
- Support for Windows systems

---
