from flask import Flask, jsonify
import RPi.GPIO as GPIO
import sqlite3
import time
import json
import atexit

# Initialize Flask app
app = Flask(__name__)

# SQLite Database File
DB_FILE = "shutters_control.db"

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

# Function to log results to the database
def save_results(test_type, value):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO performance (test_type, measured_value) VALUES (?, ?)", (test_type, value))
        conn.commit()

# Function to insert log entries
def insert_log(event):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO logs (event) VALUES (?)", (event,))
        conn.commit()

# Function to update shutter status in the database
def update_shutter_status(shutter_name, new_status):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE shutters SET status = ? WHERE name = ?", (new_status, shutter_name))
        conn.commit()

# Function to toggle shutters and measure time
def toggle_shutter(shutter_name):
    if shutter_name not in SHUTTER_PINS:
        return {"error": "Invalid shutter name"}

    pin = SHUTTER_PINS[shutter_name]

    # Retrieve current status
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM shutters WHERE name = ?", (shutter_name,))
        result = c.fetchone()

    if not result:
        return {"error": "Shutter not found"}

    current_status = result[0]
    new_status = "open" if current_status == "closed" else "closed"

    start_time = time.perf_counter()
    GPIO.output(pin, GPIO.HIGH)  # Activate shutter
    time.sleep(1)  # Simulate shutter movement
    GPIO.output(pin, GPIO.LOW)  # Deactivate shutter
    end_time = time.perf_counter()

    toggle_time = (end_time - start_time) * 1000  # Convert to milliseconds

    # Update database
    update_shutter_status(shutter_name, new_status)
    insert_log(f"Shutter {shutter_name} toggled to {new_status}")
    save_results("shutter_toggle_time", toggle_time)

    return {"shutter": shutter_name, "toggle_time_ms": round(toggle_time, 2)}

# Web response time testing
def test_web_response():
    start_time = time.perf_counter()
    end_time = time.perf_counter()
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds

    save_results("web_response_time", response_time)
    return {"response_time_ms": round(response_time, 2)}

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
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT name, status FROM shutters")
        shutters = [{"name": row[0], "status": row[1]} for row in c.fetchall()]
    return jsonify({"status": "online", "available_shutters": shutters})

# Cleanup GPIO on exit
def cleanup_gpio():
    GPIO.cleanup()
atexit.register(cleanup_gpio)

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
