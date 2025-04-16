import signal
import sys
import argparse
import asyncio
import threading
import time
from flask import Flask, request, render_template
from DbUI.database import init_db
from gpio.gpio_control import init_gpio
from gpio.sensors import monitor_sensors
from management.config import stop_event
from management.logger import log_event
from auth import auth  # Import the auth blueprint
from shutter_data import shutter_data  # Import the shutter_data blueprint

# Initialize the Flask app
app = Flask(__name__)

# Define the home route
@app.route("/home")
def home():
    access = request.args.get("access")
    if access == "true":
        # Render a page with a button to display the Flask UI
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Home</title>
            <style>
                body { font-family: Arial; text-align: center; padding-top: 50px; }
                button { padding: 10px 20px; font-size: 16px; background-color: #007BFF; color: white; border: none; cursor: pointer; }
                button:hover { background-color: #0056b3; }
                iframe { width: 80%; height: 500px; border: 1px solid #ccc; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>Welcome to the Home Page!</h1>
            <button onclick="document.getElementById('ui-frame').style.display='block'">Open Flask UI</button>
            <iframe id="ui-frame" src="/" style="display:none;"></iframe>
        </body>
        </html>
        """
    else:
        return "<h1>Access Denied</h1>"

def signal_handler(sig, frame):
    """Handle termination signals by setting the stop event."""
    log_event(f"Signal {sig} received, shutting down gracefully.")
    stop_event.set()
    time.sleep(0.5)
    sys.exit(0)

def run_sensor_monitoring():
    """Run the sensor monitoring in a dedicated thread with its own event loop."""
    log_event("Sensor monitoring thread starting...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(monitor_sensors())
    except Exception as e:
        log_event(f"Error in sensor monitoring: {e}")
    finally:
        loop.close()
        log_event("Sensor monitoring thread stopped")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Shutter Control System")
    parser.add_argument("-m", "--disable-motors", action="store_true",
                        help="Disable motor control (default: enabled)")
    parser.add_argument("-s", "--disable-sensors", action="store_true",
                        help="Disable sensor monitoring (default: enabled)")
    args = parser.parse_args()

    # Override motor control config flag
    from management import config
    config.motorControl = not args.disable_motors

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start sensor thread if not disabled
    if args.disable_sensors:
        log_event("Sensor monitoring disabled via command-line flag.")
    else:
        log_event("Sensor monitoring enabled (default setting).")
        sensor_thread = threading.Thread(target=run_sensor_monitoring, daemon=True)
        sensor_thread.start()

    # Initialize database and GPIO
    init_db()
    init_gpio()

    # Register blueprints for auth and shutter data routes
    app.secret_key = "your_super_secure_key"
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(shutter_data)

    # Run Flask app
    log_event("Flask app starting on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
