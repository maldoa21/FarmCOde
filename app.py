from flask import Flask, jsonify
import time
import requests

app = Flask(__name__)

# Number of test attempts
NUM_ATTEMPTS = 500

# Simulated Shutter Toggle Test
def test_shutter_toggle():
    times = []
    
    for _ in range(NUM_ATTEMPTS):
        start_time = time.perf_counter()
        toggle_state = not True  # Simulating a toggle
        end_time = time.perf_counter()
        
        times.append((end_time - start_time) * 1000)  # Convert to ms
    
    return {
        "average_toggle_time_ms": sum(times) / NUM_ATTEMPTS,
        "min_toggle_time_ms": min(times),
        "max_toggle_time_ms": max(times)
    }

# Web Response Time Test
def test_web_response():
    times = []
    successes = 0

    for _ in range(NUM_ATTEMPTS):
        start_time = time.perf_counter()
        
        try:
            response = requests.get("http://127.0.0.1:5000/ping")  # Ping local server
            success = response.status_code == 200
            if success:
                successes += 1
        except requests.exceptions.RequestException:
            success = False
        
        end_time = time.perf_counter()
        times.append((end_time - start_time) * 1000)  # Convert to ms
    
    return {
        "success_rate": (successes / NUM_ATTEMPTS) * 100,
        "average_response_time_ms": sum(times) / NUM_ATTEMPTS,
        "min_response_time_ms": min(times),
        "max_response_time_ms": max(times)
    }

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
