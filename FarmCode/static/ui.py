from flask import Flask, render_template, jsonify, url_for
import random
import threading
import sqlite3

from gpio.shutters import operate_shutter, cancel_shutter_operation, operation_intended_actions
from DbUI.database import update_shutter_status, get_shutter_status
from management.logger import log_event
import gpio.gpio_control
from management.config import DB_FILE

app = Flask(__name__)

def get_temperature() -> float:
    """Simulate a temperature measurement."""
    return round(random.uniform(60, 85), 2)

@app.route("/")
def index():
    # Fetch status from DB so the page shows it immediately
    slug_shutter_status = get_shutter_status("Slug Shutter")
    slug_sidewall_status = get_shutter_status("Slug Sidewall")
    return render_template(
        "index.html",
        temperature=get_temperature(),
        slug_shutter_status=slug_shutter_status,
        slug_sidewall_status=slug_sidewall_status
    )

@app.route("/temperature")
def temperature():
    # Optionally add headers to prevent caching
    response = jsonify({"temperature": get_temperature()})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route("/change_status/<device>/<action>", methods=["POST"])
def change_status(device, action):
    device = device.strip()
    action = action.strip().lower()
    if action not in ["open", "close", "automatic"]:
        return jsonify({"message": "Invalid action."}), 400

    current_status = get_shutter_status(device)

    if action == "automatic":
        if current_status == "live":
            log_event(f"Cancelling live operation for {device} to initiate automatic mode.")
            cancel_shutter_operation(device)
        update_shutter_status(device, "automatic")
        log_event(f"Automatic operation requested for {device}.")
        return jsonify({"message": f"{device} set to automatic mode."})

    if current_status == action and current_status != "live":
        return jsonify({"message": f"{device} is already {action}."})

    if current_status == "live":
        current_live_action = operation_intended_actions.get(device)
        if current_live_action == action:
            return jsonify({"message": f"{device} is already {action}."})
        else:
            log_event(f"Cancelling live operation for {device} to initiate {action}.")
            cancel_shutter_operation(device)
            update_shutter_status(device, "live")
            threading.Thread(target=operate_shutter, args=(device, action), daemon=True).start()
            return jsonify({"message": f"{device} switching to {action} operation initiated."})

    update_shutter_status(device, "live")
    log_event(f"Manual operation requested for {device}.")
    threading.Thread(target=operate_shutter, args=(device, action), daemon=True).start()
    return jsonify({"message": f"{device} set to {action} operation initiated."})

@app.route("/status/<device>")
def status(device):
    device = device.strip()
    current_status = get_shutter_status(device)
    response = jsonify({"status": current_status})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route("/active_motor_count")
def active_motor_count():
    return jsonify({"count": gpio.gpio_control.active_motor_count})

# ✅ NEW: Show full shutter log data
@app.route("/shutter-data")
def shutter_data():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT timestamp, event FROM logs ORDER BY timestamp DESC")
            logs = c.fetchall()
    except Exception as e:
        logs = []
        log_event(f"ERROR fetching shutter logs: {e}")
    return render_template("shutter_data.html", logs=logs)
