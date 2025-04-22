from flask import Blueprint, render_template
from datetime import datetime, timedelta

shutter_data = Blueprint("shutter_data", __name__)

@shutter_data.route("/shutter-data")
def view_full_log():
    logs = [
        ("2025-04-08 07:30 AM", "Slug Shutter opened manually"),
        ("2025-04-08 08:15 AM", "Slug Sidewall closed automatically"),
        ("2025-04-08 09:05 AM", "Slug Shutter set to automatic mode"),
        ("2025-04-08 10:22 AM", "Slug Sidewall opened manually"),
        ("2025-04-08 11:45 AM", "Slug Shutter closed manually"),
        ("2025-04-08 01:03 PM", "Slug Sidewall set to automatic mode"),
        ("2025-04-08 03:30 PM", "Slug Shutter opened automatically"),
        ("2025-04-08 04:10 PM", "Slug Sidewall closed manually"),
        ("2025-04-08 05:00 PM", "Slug Shutter set to automatic mode")
    ]

    temperature_logs = [
        ("2025-04-08 07:00 AM", "72.5 °F"),
        ("2025-04-08 08:00 AM", "74.3 °F"),
        ("2025-04-08 09:00 AM", "75.8 °F"),
        ("2025-04-08 10:00 AM", "77.1 °F"),
        ("2025-04-08 11:00 AM", "78.4 °F"),
        ("2025-04-08 12:00 PM", "79.9 °F"),
        ("2025-04-08 01:00 PM", "81.2 °F"),
        ("2025-04-08 02:00 PM", "80.3 °F"),
        ("2025-04-08 03:00 PM", "78.7 °F")
    ]

    # Filter logs for the last 24 hours
    now = datetime.now()
    last_24_hours_logs = []
    for timestamp_str, event in logs:
        try:
            log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %I:%M %p")
            if now - log_time <= timedelta(hours=24):
                last_24_hours_logs.append((timestamp_str, event))
        except ValueError as e:
            print(f"[WARNING] Timestamp format issue: {timestamp_str} – {e}")

    return render_template(
        "shutter_log.html",
        logs=logs,
        temperature_logs=temperature_logs,
        last_24_hours_logs=last_24_hours_logs
    )
