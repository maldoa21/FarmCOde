import sqlite3

DB_FILE = "shutters_control.db"

def init_db():
    """Initialize the SQLite database using the schema."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        with open("shutters_control.sql", "r") as f:
            c.executescript(f.read())
        conn.commit()

def insert_log(event):
    """Insert an event log into the database."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO logs (event) VALUES (?)", (event,))
        conn.commit()

def update_shutter_status(shutter_name, new_status):
    """Update the status of a shutter."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE shutters SET status = ? WHERE name = ?", (new_status, shutter_name))
        conn.commit()

def insert_performance_data(test_type, value):
    """Store performance test results."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO performance (test_type, measured_value) VALUES (?, ?)", (test_type, value))
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
