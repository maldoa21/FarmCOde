-- Create the database structure

-- Table to store shutters
CREATE TABLE IF NOT EXISTS shutters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open', 'closed'))
);

-- Table to store action logs
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event TEXT NOT NULL
);

-- Table to store performance test results
CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_type TEXT NOT NULL,
    measured_value REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial shutter states
INSERT OR IGNORE INTO shutters (name, status) VALUES
    ('shutter_1', 'closed'),
    ('shutter_2', 'closed');
