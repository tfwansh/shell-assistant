# Shell Assistant

A local app that interprets natural language and safely executes shell commands on Linux and macOS. Powered by Ollama and LLMs for robust, platform-aware command generation.

## Features
- Natural language to shell command (Linux/macOS aware)
- Command confirmation before execution
- Safety checks to prevent dangerous operations
- Modern, responsive web UI

## Quick Start

```sh
git clone https://github.com/PSxUchiha/shell-assistant.git
cd shell-assistant
# For Linux:
bash <(curl -fsSL https://raw.githubusercontent.com/PSxUchiha/shell-assistant/master/scripts/quickstart-linux.sh)
# For macOS:
bash <(curl -fsSL https://raw.githubusercontent.com/PSxUchiha/shell-assistant/master/scripts/quickstart-macos.sh)
```

## Manual Setup
1. **Install [Ollama](https://ollama.com/download) and run a model:**
   ```sh
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   # macOS
   brew install ollama
   ollama pull deepseek-coder
   ollama serve &
   ```
2. **Create a Python venv and install dependencies:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```sh
   python main.py
   # Visit http://localhost:5000
   ```

## Requirements
- Python 3.8+
- Ollama (running locally)
- Model: `deepseek-coder` (recommended)
- Linux or macOS

## Usage
- Enter a natural language command in the web UI.
- Review the interpreted shell command and notes.
- Confirm to execute, or cancel.
- View output and errors in the UI.

## Security
- Commands are checked for safety before execution.
- No commands are run without explicit user confirmation.

## License
MIT
