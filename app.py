from flask import Flask, jsonify
import time
import requests

app = Flask(__name__)

# Simulated Shutter Toggle Test
def test_shutter_toggle():
    start_time = time.perf_counter()
    toggle_state = not True  # Simulating a toggle
    end_time = time.perf_counter()
    
    toggle_time = (end_time - start_time) * 1000  # Convert to ms
    return {"shutter_toggle_time_ms": toggle_time}

# Web Response Time Test
def test_web_response():
    start_time = time.perf_counter()
    
    try:
        response = requests.get("http://127.0.0.1:5000/ping")  # Ping local server
        success = response.status_code == 200
    except requests.exceptions.RequestException:
        success = False
    
    end_time = time.perf_counter()
    response_time = (end_time - start_time) * 1000  # Convert to ms
    
    return {"success": success, "response_time_ms": response_time}

@app.route('/test/shutter')
def shutter_test():
    return jsonify(test_shutter_toggle())

@app.route('/test/web')
def web_test():
    return jsonify(test_web_response())

@app.route('/ping')
def ping():
    return jsonify({"status": "ok"})  # Used to test web response time

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
