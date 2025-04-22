from flask import Flask, render_template, jsonify, url_for
import random
import threading
import sqlite3
from datetime import datetime, timedelta

from gpio.shutters import operate_shutter, cancel_shutter_operation, operation_intended_actions
from DbUI.database import update_shutter_status, get_shutter_status
from management.logger import log_event
import gpio.gpio_control
from management.config import DB_FILE

app = Flask(__name__)

def get_temperature() -> float:
    return round(random.uniform(60, 85), 2)

def insert_log_event(event: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO logs (timestamp, event) VALUES (?, ?)", (timestamp, event))
            conn.commit()
    except Exception as e:
        log_event(f"[ERROR] Failed to insert log event: {e}")

@app.route("/")
def index():
    slug_shutter_status = get_shutter_status("Slug Shutter")
    slug_sidewall_status = get_shutter_status("Slug Sidewall")

    recent_logs = []
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT timestamp, event FROM logs ORDER BY timestamp DESC")
            all_logs = c.fetchall()

            now = datetime.now()
            for ts_str, event in all_logs:
                try:
                    log_time = datetime.strptime(ts_str, "%Y-%m-%d %I:%M %p")
                    if now - log_time <= timedelta(hours=24):
                        recent_logs.append((ts_str, event))
                except Exception as e:
                    log_event(f"Invalid timestamp in log: {ts_str} - {e}")
    except Exception as e:
        log_event(f"Error fetching logs for home page: {e}")

    return render_template(
        "index.html",
        temperature=get_temperature(),
        slug_shutter_status=slug_shutter_status,
        slug_sidewall_status=slug_sidewall_status,
        recent_logs=recent_logs
    )

@app.route("/temperature")
def temperature():
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
        insert_log_event(f"{device} set to automatic mode via UI button")
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
            insert_log_event(f"{device} switching to {action} via UI button")
            threading.Thread(target=operate_shutter, args=(device, action), daemon=True).start()
            return jsonify({"message": f"{device} switching to {action} operation initiated."})

    update_shutter_status(device, "live")
    log_event(f"Manual operation requested for {device}.")
    insert_log_event(f"{device} set to {action} via UI button")
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
