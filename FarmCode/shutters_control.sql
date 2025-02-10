-- Create the database schema for the Shutter Control System

-- Create a table for users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL -- e.g., "admin" or "user"
);

-- Create a table for shutter settings
CREATE TABLE IF NOT EXISTS shutters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- Name of the shutter (e.g., "Living Room Shutter")
    status TEXT NOT NULL CHECK (status IN ('open', 'closed', 'manual')), -- Current status
    position INTEGER CHECK (position BETWEEN 0 AND 100), -- Position percentage (0 = fully closed, 100 = fully open)
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for manual control logs
CREATE TABLE IF NOT EXISTS manual_control_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shutter_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('open', 'close', 'adjust')), -- The action performed
    position INTEGER CHECK (position BETWEEN 0 AND 100), -- Target position for the action
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    performed_by INTEGER NOT NULL, -- References the user who performed the action
    FOREIGN KEY (shutter_id) REFERENCES shutters (id),
    FOREIGN KEY (performed_by) REFERENCES users (id)
);

-- Insert sample data into users
INSERT INTO users (username, password, role) VALUES 
('admin', 'admin123', 'admin'),
('user1', 'password1', 'user');

-- Insert sample data into shutters
INSERT INTO shutters (name, status, position) VALUES 
('Living Room Shutter', 'open', 100),
('Bedroom Shutter', 'closed', 0),
('Kitchen Shutter', 'manual', 50);

-- Insert sample data into manual control logs
INSERT INTO manual_control_logs (shutter_id, action, position, performed_by) VALUES 
(1, 'adjust', 75, 1),
(2, 'open', 100, 2),
(3, 'close', 0, 1);

-- Query to verify data
SELECT * FROM users;
SELECT * FROM shutters;
SELECT * FROM manual_control_logs;
