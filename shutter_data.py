from flask import Blueprint, render_template_string
import sqlite3
from datetime import datetime, timedelta
import random
from management.config import DB_FILE

shutter_data = Blueprint("shutter_data", __name__)

def get_all_logs():
    """
    Retrieve all log entries from the database.
    """
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT timestamp, event FROM logs ORDER BY timestamp DESC")
        return c.fetchall()

def insert_fake_logs():
    """
    Populate the database with fake logs for UI demonstration purposes.
    Includes both shutter actions and temperature logs.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Ensure logs table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event TEXT NOT NULL
            );
        ''')

        # Optional: Clear existing logs
        cursor.execute("DELETE FROM logs")

        now = datetime.now()

        # Shutter operation logs
        shutter_logs = [
            (now - timedelta(hours=23), "Slug Shutter opened manually"),
            (now - timedelta(hours=21), "Slug Sidewall closed automatically"),
            (now - timedelta(hours=19), "Slug Shutter set to automatic mode"),
            (now - timedelta(hours=16), "Slug Sidewall opened manually"),
            (now - timedelta(hours=12), "Slug Shutter closed manually"),
            (now - timedelta(hours=8), "Slug Sidewall set to automatic mode"),
            (now - timedelta(hours=4), "Slug Shutter opened automatically"),
            (now - timedelta(hours=2), "Slug Sidewall closed manually"),
            (now - timedelta(hours=1), "Slug Shutter set to automatic mode")
        ]

        # Temperature reading logs
        temperature_logs = [
            (now - timedelta(hours=22), f"Temperature reading: {round(random.uniform(65, 85), 2)} °F"),
            (now - timedelta(hours=18), f"Temperature reading: {round(random.uniform(65, 85), 2)} °F"),
            (now - timedelta(hours=14), f"Temperature reading: {round(random.uniform(65, 85), 2)} °F"),
            (now - timedelta(hours=10), f"Temperature reading: {round(random.uniform(65, 85), 2)} °F"),
            (now - timedelta(hours=6), f"Temperature reading: {round(random.uniform(65, 85), 2)} °F"),
            (now - timedelta(hours=2), f"Temperature reading: {round(random.uniform(65, 85), 2)} °F"),
        ]

        # Combine and sort
        combined_logs = shutter_logs + temperature_logs
        combined_logs.sort(key=lambda x: x[0])

        # Insert into DB
        cursor.executemany(
            "INSERT INTO logs (timestamp, event) VALUES (?, ?)",
            [(ts.strftime('%Y-%m-%d %H:%M:%S'), msg) for ts, msg in combined_logs]
        )

        conn.commit()

# Only insert fake logs when this file is run directly (optional)
if __name__ == "__main__":
    insert_fake_logs()
    print("✅ Fake shutter and temperature logs inserted.")

# Route to display full log page
@shutter_data.route("/shutter-data")
def view_full_log():
    logs = get_all_logs()
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Full Shutter Log</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 20px; }
            table { margin: auto; border-collapse: collapse; width: 80%; background: white; }
            th, td { padding: 10px; border: 1px solid #ccc; }
            th { background-color: #007BFF; color: white; }
        </style>
    </head>
    <body>
        <h1>Full Shutter Log</h1>
        <table>
            <tr><th>Timestamp</th><th>Event</th></tr>
            {% for log in logs %}
            <tr><td>{{ log[0] }}</td><td>{{ log[1] }}</td></tr>
            {% endfor %}
        </table>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """
    return render_template_string(html, logs=logs)
