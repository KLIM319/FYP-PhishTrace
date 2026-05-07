import subprocess
import requests
import time
import os
import threading
import platform
import re

# Import the Flask app directly
from payload.beacon_server import app as beacon_app

# Global variables
flask_thread = None
tunnel_process = None
active_tunnel_url = None

def start_flask():
    """Runs the Flask server silently without spawning new processes."""
    beacon_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_infrastructure():
    """Starts the Flask beacon server and Tunnelmole, then fetches the dynamic URL."""
    global flask_thread, tunnel_process, active_tunnel_url
    
    if active_tunnel_url:
        return True, active_tunnel_url

    try:
        # 1. Start the Flask Beacon Server
        if flask_thread is None or not flask_thread.is_alive():
            flask_thread = threading.Thread(target=start_flask, daemon=True)
            flask_thread.start()
        
        # 2. Start Tunnelmole using npx (Cross-Platform)
        print("[*] Spawning Tunnelmole...")
        
        # We use npx to ensure it runs smoothly on macOS
        tunnel_process = subprocess.Popen(
            ["npx", "tunnelmole", "5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # 3. Read the terminal output to extract the secure HTTPS URL
        for line in iter(tunnel_process.stdout.readline, ''):
            # Tunnelmole prints: "https://random-string.tunnelmole.net is forwarding to localhost:5000"
            match = re.search(r"(https://[a-zA-Z0-9-]+\.tunnelmole\.net)", line)
            
            if match:
                active_tunnel_url = match.group(1)
                print(f"[+] Infrastructure Online! Dynamic Link: {active_tunnel_url}")
                return True, active_tunnel_url
                
            # Failsafe if it hangs or errors
            if "error" in line.lower() or "failed" in line.lower():
                print(f"[-] Tunnelmole Error: {line.strip()}")
                return False, "Tunnelmole failed to start."

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Server failed to start: {e}\n")
        return False, f"Infrastructure startup failed: {e}"
    
def check_status():
    """Checks if the Tunnel is active."""
    global active_tunnel_url
    if active_tunnel_url:
        return True, active_tunnel_url
    return False, "Offline"

def stop_infrastructure():
    """Kills the background servers when the app closes."""
    global tunnel_process, active_tunnel_url
    
    if tunnel_process:
        tunnel_process.kill()
    active_tunnel_url = None