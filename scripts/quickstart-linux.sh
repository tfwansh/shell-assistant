#!/bin/bash
set -e

# Quickstart script for Shell Assistant (Linux)

# 1. Install Ollama if not present
if ! command -v ollama &> /dev/null; then
  echo "Ollama not found. Installing..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

# 2. Start Ollama in the background (if not running)
if ! pgrep -x "ollama" > /dev/null; then
  echo "Starting Ollama..."
  nohup ollama serve > ollama.log 2>&1 &
  sleep 2
fi

# 3. Pull recommended model
ollama pull deepseek-coder

# 4. Set up Python venv
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Start the app
python main.py 