from flask import Flask, jsonify
import time
import sqlite3
import atexit

# Initialize Flask app
app = Flask(__name__)

# SQLite Database File
DB_FILE = "shutters_control.db"

# Function to initialize the database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS shutters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        status TEXT NOT NULL CHECK(status IN ('open', 'closed'))
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        event TEXT NOT NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_type TEXT NOT NULL,
                        measured_value REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
        # Insert default shutters if they don't exist
        c.execute("INSERT OR IGNORE INTO shutters (name, status) VALUES ('shutter_1', 'closed'), ('shutter_2', 'closed')")
        conn.commit()

# Initialize the database
init_db()

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
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM shutters WHERE name = ?", (shutter_name,))
        result = c.fetchone()

    if not result:
        return {"error": "Shutter not found"}

    current_status = result[0]
    new_status = "open" if current_status == "closed" else "closed"

    start_time = time.perf_counter()
    time.sleep(1)  # Simulating the time required to toggle a real shutter
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

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
