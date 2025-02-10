from flask import Flask, jsonify
from gpiozero import LED
import time

app = Flask(__name__)

# GPIO Pin Setup
SHUTTER_PIN = 17  # GPIO Pin for the shutter (adjust as needed)
shutter = LED(SHUTTER_PIN)

@app.route('/toggle_shutter', methods=['GET'])
def toggle_shutter():
    """Toggles the shutter and measures the time taken for the action."""
    start_time = time.time()  # Start timing

    # Toggle the shutter
    shutter.on()
    time.sleep(0.5)  # Simulated delay for the shutter movement
    shutter.off()

    toggle_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    return jsonify({"status": "success", "toggle_time_ms": toggle_time})

@app.route('/status', methods=['GET'])
def status():
    """Returns the server status and confirms it's running."""
    return jsonify({"status": "running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
