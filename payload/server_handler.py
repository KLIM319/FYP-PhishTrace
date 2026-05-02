import subprocess
import requests
import time
import os
import threading
import platform

# 🚀 THE FIX 1: Import the Flask app directly instead of opening a new program!
from payload.beacon_server import app as beacon_app

# Global variables
flask_thread = None
ngrok_process = None
active_ngrok_url = None

def start_flask():
    """Runs the Flask server silently without spawning new processes."""
    # use_reloader=False is CRITICAL when running Flask inside a compiled .exe
    beacon_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_infrastructure():
    """Starts the Flask beacon server and Ngrok, then fetches the dynamic URL."""
    global flask_thread, ngrok_process, active_ngrok_url
    
    # Don't restart if it's already running
    if active_ngrok_url:
        return True, active_ngrok_url

    try:
        # 1. Start the Flask Beacon Server in a silent background thread
        if flask_thread is None or not flask_thread.is_alive():
            flask_thread = threading.Thread(target=start_flask, daemon=True)
            flask_thread.start()
        
        # 2. Start Ngrok on port 5000 (🚀 CROSS-PLATFORM FIX)
        current_os = platform.system()
        
        if current_os == "Windows":
            # Windows Logic
            ngrok_path = os.path.join(os.path.dirname(__file__), 'ngrok.exe')
            CREATE_NO_WINDOW = 0x08000000
            ngrok_process = subprocess.Popen(
                [ngrok_path, "http", "5000"],  
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW  # Applies the hidden window fix
            )
        else:
            # Mac / Linux Logic
            ngrok_path = os.path.join(os.path.dirname(__file__), 'ngrok')
            ngrok_process = subprocess.Popen(
                [ngrok_path, "http", "5000"],  
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
                # 🚀 CRITICAL: We removed 'creationflags' because it crashes Mac!
            )
        
        # 3. Wait a few seconds for Ngrok to establish the tunnel
        time.sleep(3)
        
        # 4. Fetch the dynamic URL from Ngrok's local API
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        data = response.json()
        
        # Extract the secure HTTPS URL
        for tunnel in data['tunnels']:
            if tunnel['public_url'].startswith("https"):
                active_ngrok_url = tunnel['public_url']
                break
                
        if active_ngrok_url:
            print(f"[+] Infrastructure Online! Dynamic Link: {active_ngrok_url}")
            return True, active_ngrok_url
        else:
            return False, "Failed to parse Ngrok URL."

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Server failed to start: {e}\n")
        return False, f"Infrastructure startup failed: {e}"
    
def check_status():
    """Checks if Ngrok is actively running and returns the URL."""
    global active_ngrok_url
    if active_ngrok_url:
        try:
            requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
            return True, active_ngrok_url
        except Exception:
            active_ngrok_url = None
            return False, "Offline"
    return False, "Offline"

def stop_infrastructure():
    """Kills the background servers when the app closes."""
    global ngrok_process, active_ngrok_url
    
    # We only need to kill Ngrok. 
    # The Flask thread is a 'daemon', so it dies automatically when the app closes.
    if ngrok_process:
        ngrok_process.kill()
    active_ngrok_url = None