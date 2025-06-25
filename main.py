import os
import sys
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import subprocess
import signal

# Import our custom modules
from distro_detector import get_distro_info
from command_executor import execute_command, is_safe_command, filter_unnecessary_sudo
from ollama_interface import interpret_command
from user_info import get_user_info

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get distribution and user info at startup
DISTRO_INFO = get_distro_info()
USER_INFO = get_user_info()

print(f"Detected system distribution:\n{DISTRO_INFO}")
print(f"User information:\n{USER_INFO}")

# Track running processes per session
running_processes = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/interpret', methods=['POST'])
def interpret():
    user_input = request.json.get('command', '')
    print(f"User input (interpret): {user_input}")
    try:
        command_output = interpret_command(user_input, DISTRO_INFO, USER_INFO)
        command = command_output.command
        notes = command_output.notes
        if command_output.requires_sudo:
            if notes:
                notes = f"This command requires sudo privileges. {notes}"
            else:
                notes = "This command requires sudo privileges."
        print(f"Interpreted command: {command}")
        print(f"Notes: {notes}")
        return jsonify({
            'interpreted_command': command,
            'notes': notes
        })
    except Exception as e:
        return jsonify({
            'interpreted_command': f"echo 'Error: {str(e)}'",
            'notes': f"An error occurred: {str(e)}"
        }), 400

# Remove the old /execute route
# Add SocketIO event for command execution
@socketio.on('execute_command')
def handle_execute_command(data):
    shell_command = data.get('command', '')
    model_name = data.get('model', 'deepseek-coder')
    sid = request.sid
    print(f"[WS] User input (execute): {shell_command} | Model: {model_name}")
    if not is_safe_command(shell_command):
        socketio.emit('command_output', {'line': 'This command requires manual intervention for safety reasons.'}, room=sid)
        socketio.emit('command_complete', {}, room=sid)
        return
    def run_and_stream():
        try:
            # Change to user's home directory before executing
            os.chdir(USER_INFO['home'])
            env = os.environ.copy()
            env['HOME'] = USER_INFO['home']
            env['USER'] = USER_INFO['username']
            # Start subprocess with pipes for interactive I/O
            process = subprocess.Popen(
                shell_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=1,
                preexec_fn=os.setsid
            )
            running_processes[sid] = process
            def send_line(line):
                socketio.emit('command_output', {'line': line}, room=sid)
            for line in iter(process.stdout.readline, ''):
                if line:
                    send_line(line.rstrip('\n'))
            process.stdout.close()
            process.wait()
            socketio.emit('command_complete', {'returncode': process.returncode}, room=sid)
        except Exception as e:
            socketio.emit('command_output', {'line': f'Error: {str(e)}'}, room=sid)
            socketio.emit('command_complete', {}, room=sid)
        finally:
            running_processes.pop(sid, None)
    thread = threading.Thread(target=run_and_stream)
    thread.start()

@socketio.on('stop_command')
def handle_stop_command():
    sid = request.sid
    process = running_processes.get(sid)
    if process and process.poll() is None:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except Exception as e:
            print(f"Error killing process group: {e}")
        socketio.emit('command_output', {'line': '[Process terminated by user]'}, room=sid)
        socketio.emit('command_complete', {'returncode': -1}, room=sid)
        running_processes.pop(sid, None)

@socketio.on('send_input')
def handle_send_input(data):
    # This is a placeholder for interactive input support. To fully support interactive commands, you would need to keep track of the process and write to its stdin.
    pass

def test_cli_mode():
    """Simple CLI mode for testing without web interface"""
    print("Command Assistant CLI Mode")
    print(f"System: {DISTRO_INFO.splitlines() if isinstance(DISTRO_INFO, str) else DISTRO_INFO}")
    
    while True:
        user_input = input("\nEnter command in natural language (or 'exit' to quit): ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        try:
            # Use structured output for command interpretation
            command_output = interpret_command(user_input, DISTRO_INFO, USER_INFO)
            command = command_output.command
            notes = command_output.notes
            
            # Add sudo warning if needed
            if command_output.requires_sudo:
                if notes:
                    notes = f"This command requires sudo privileges. {notes}"
                else:
                    notes = "This command requires sudo privileges."
            
            print(f"\nInterpreted command: {command}")
            
            if notes:
                print(f"Notes: {notes}")
            
            if not is_safe_command(command):
                print("This command requires manual intervention for safety reasons.")
                continue
                
            proceed = input("Execute this command? (y/n): ")
            if proceed.lower() != 'y':
                continue
                
            result = execute_command(command, USER_INFO)
            if isinstance(result, dict):
                print("\nOutput:")
                if result['stdout']:
                    print(result['stdout'])
                if result['stderr']:
                    print("Errors:")
                    print(result['stderr'])
                print(f"Return code: {result['returncode']}")
            else:
                print(f"\nResult: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

if __name__ == '__main__':
    # Check if CLI mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        test_cli_mode()
    else:
        print("Starting web interface on http://127.0.0.1:5000")
        socketio.run(app, debug=True)

