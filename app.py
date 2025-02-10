from flask import Flask, jsonify
import RPi.GPIO as GPIO
import time
import json

# Initialize Flask app
app = Flask(__name__)

# GPIO Setup
SHUTTER_PINS = {
    "shutter_1": 17,  # Adjust these GPIO pins based on your wiring
    "shutter_2": 27
}

GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
GPIO.setwarnings(False)

# Set all shutter pins as output
for pin in SHUTTER_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Ensure all shutters start in the OFF position

# Function to log results
def save_results(filename, data):
    with open(filename, "a") as file:
        file.write(json.dumps(data) + "\n")

# Function to toggle shutters and measure time
def toggle_shutter(shutter_name):
    if shutter_name not in SHUTTER_PINS:
        return {"error": "Invalid shutter name"}
    
    pin = SHUTTER_PINS[shutter_name]
    
    start_time = time.perf_counter()
    GPIO.output(pin, GPIO.HIGH)  # Activate shutter
    time.sleep(1)  # Simulate shutter movement
    GPIO.output(pin, GPIO.LOW)  # Deactivate shutter
    end_time = time.perf_counter()
    
    toggle_time = (end_time - start_time) * 1000  # Convert to milliseconds
    result = {"shutter": shutter_name, "toggle_time_ms": round(toggle_time, 2)}
    
    save_results("shutter_results.json", result)
    return result

# Web response time testing
def test_web_response():
    start_time = time.perf_counter()
    end_time = time.perf_counter()
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    result = {"response_time_ms": round(response_time, 2)}
    save_results("web_results.json", result)
    return result

# Flask Routes
@app.route("/")
def home():
    return "Shutter Control System Running", 200

@app.route("/toggle/<shutter_name>")
def toggle(shutter_name):
    return jsonify(toggle_shutter(shutter_name))

@app.route("/test/web")
def web_test():
    return jsonify(test_web_response())

@app.route("/status")
def status():
    return jsonify({"status": "online", "available_shutters": list(SHUTTER_PINS.keys())})

# Cleanup GPIO on exit
import atexit
def cleanup_gpio():
    GPIO.cleanup()
atexit.register(cleanup_gpio)

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
