from flask import Flask, jsonify
import time
import requests
import json

app = Flask(__name__)

# Number of test attempts
NUM_ATTEMPTS = 500

# Function to save results to a log file
def save_results(filename, data):
    with open(filename, "a") as file:
        file.write(json.dumps(data) + "\n")

# Simulated Shutter Toggle Test
def test_shutter_toggle():
    times = []
    
    for _ in range(NUM_ATTEMPTS):
        start_time = time.perf_counter()
        toggle_state = not True  # Simulating a toggle
        end_time = time.perf_counter()
        
        times.append((end_time - start_time) * 1000)  # Convert to ms
    
    results = {
        "average_toggle_time_ms": sum(times) / NUM_ATTEMPTS,
        "min_toggle_time_ms": min(times),
        "max_toggle_time_ms": max(times)
    }
    save_results("shutter_results.json", results)
    return results

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
    
    results = {
        "success_rate": (successes / NUM_ATTEMPTS) * 100,
        "average_response_time_ms": sum(times) / NUM_ATTEMPTS,
        "min_response_time_ms": min(times),
        "max_response_time_ms": max(times)
    }
    save_results("web_results.json", results)
    return results

@app.route("/")
def home():
    return "Raspberry Pi Web Test Server is Running", 200

@app.route("/test/shutter")
def shutter_test():
    return jsonify(test_shutter_toggle())

@app.route("/test/web")
def web_test():
    return jsonify(test_web_response())

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})  # Used to test web response time

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
