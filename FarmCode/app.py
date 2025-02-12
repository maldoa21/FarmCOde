from flask import Flask, render_template_string, jsonify
import time
import sqlite3
import datetime
import random

# Initialize Flask app ps
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
                        status TEXT NOT NULL CHECK(status IN ('open', 'closed', 'automatic'))
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
        c.execute("INSERT OR IGNORE INTO shutters (name, status) VALUES ('Slug Sidewall', 'closed'), ('Slug Shutter', 'closed')")
        conn.commit()

# Initialize the database
init_db()

# Function to log events
def insert_log(event):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO logs (event) VALUES (?)", (event,))
        conn.commit()

# Function to update shutter status
def update_shutter_status(shutter_name, new_status):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE shutters SET status = ? WHERE name = ?", (new_status, shutter_name))
        conn.commit()

# Function to simulate getting a temperature reading
def get_temperature():
    return round(random.uniform(50.0, 90.0), 2)  # Simulated Fahrenheit reading

# Function to change shutter status
def change_shutter_status(shutter_name, new_status):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM shutters WHERE name = ?", (shutter_name,))
        result = c.fetchone()

    if not result:
        return {"error": "Shutter not found"}

    # Simulate processing delay for status change
    time.sleep(1)

    # Update database
    update_shutter_status(shutter_name, new_status)
    insert_log(f"Shutter '{shutter_name}' changed to {new_status}")

    return {"shutter": shutter_name, "new_status": new_status}

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
                width: 70%;
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
            .action-buttons {
                display: flex;
                justify-content: center;
                gap: 10px;
            }
            .action-button {
                padding: 8px 15px;
                font-size: 14px;
                color: white;
                border: none;
                cursor: pointer;
                border-radius: 5px;
            }
            .open-btn { background: green; }
            .close-btn { background: red; }
            .auto-btn { background: orange; }
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
                <td class="action-buttons">
                    <button class="action-button open-btn" onclick="changeStatus('{{ shutter.name }}', 'open')">Open</button>
                    <button class="action-button close-btn" onclick="changeStatus('{{ shutter.name }}', 'closed')">Close</button>
                    <button class="action-button auto-btn" onclick="changeStatus('{{ shutter.name }}', 'automatic')">Automatic</button>
                </td>
            </tr>
            {% endfor %}
        </table>

        <script>
            function changeStatus(shutterName, newStatus) {
                fetch('/change_status/' + shutterName + '/' + newStatus)
                    .then(response => response.json())
                    .then(data => {
                        alert('Shutter: ' + data.shutter + ' changed to ' + data.new_status);
                        location.reload();
                    })
                    .catch(error => console.error('Error:', error));
            }
        </script>
    </body>
    </html>
    """

    return render_template_string(html_template, shutters=shutters, current_time=current_time, temperature=temperature)

@app.route("/change_status/<shutter_name>/<new_status>")
def change_status(shutter_name, new_status):
    if new_status not in ["open", "closed", "automatic"]:
        return jsonify({"error": "Invalid status"}), 400
    return jsonify(change_shutter_status(shutter_name, new_status))

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
