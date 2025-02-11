from flask import Flask, render_template_string, jsonify
import time
import sqlite3
import datetime
import random

# Initialize Flask app y
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
        c.execute("INSERT OR IGNORE INTO shutters (name, status) VALUES ('Shutter 1', 'closed'), ('Shutter 2', 'closed')")
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

# Function to simulate getting a temperature reading
def get_temperature():
    return round(random.uniform(50.0, 90.0), 2)  # Simulated Fahrenheit reading

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
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT name, status FROM shutters")
        shutters = [{"name": row[0], "status": row[1]} for row in c.fetchall()]

    current_time = datetime.datetime.now().strftime("%I:%M %p, %m/%d/%Y")  # US format, 12-hour clock
    temperature = get_temperature()  # Simulated temperature value

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Shutter Control System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #f4f4f4;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            table {
                width: 60%;
                margin: 0 auto;
                border-collapse: collapse;
                background: white;
            }
            th, td {
                padding: 12px;
                border: 1px solid #ddd;
            }
            th {
                background-color: #007BFF;
                color: white;
            }
            .toggle-button {
                padding: 10px 15px;
                font-size: 14px;
                color: white;
                background: green;
                border: none;
                cursor: pointer;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <h1>Shutter Control System</h1>
        <p><strong>Current Time:</strong> {{ current_time }}</p>
        <p><strong>Current Temperature:</strong> {{ temperature }}°F</p>
        
        <table>
            <tr>
                <th>Shutter Name</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
            {% for shutter in shutters %}
            <tr>
                <td>{{ shutter.name }}</td>
                <td>{{ shutter.status }}</td>
                <td>
                    <button class="toggle-button" onclick="toggleShutter('{{ shutter.name }}')">Toggle</button>
                </td>
            </tr>
            {% endfor %}
        </table>

        <script>
            function toggleShutter(shutterName) {
                fetch('/toggle/' + shutterName)
                    .then(response => response.json())
                    .then(data => {
                        alert('Toggled: ' + data.shutter + ' (Toggle Time: ' + data.toggle_time_ms + 'ms)');
                        location.reload();
                    })
                    .catch(error => console.error('Error:', error));
            }
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html_template, shutters=shutters, current_time=current_time, temperature=temperature)

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
