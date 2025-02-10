from gpiozero import LED
from gpiozero.pins.lgpio import LGPIOFactory
from flask import Flask, jsonify
import time

# Use LGPIOFactory to prevent GPIO conflicts
pin_factory = LGPIOFactory()

# Define GPIO pins
SHUTTER_PIN = 17

# Initialize LED object (representing the shutter toggle)
shutter = LED(SHUTTER_PIN, pin_factory=pin_factory)

# Create Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "Raspberry Pi GPIO Test Server is Running", 200

@app.route("/toggle_shutter")
def toggle_shutter():
    """Toggle the shutter and measure toggle time."""
    start_time = time.time()
    shutter.on()
    time.sleep(0.5)  # Simulate action delay
    shutter.off()
    toggle_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    return jsonify({
        "status": "Shutter toggled",
        "toggle_time_ms": round(toggle_time, 2)
    })

@app.route("/web_response_test")
def web_response_test():
    """Measure web response time."""
    start_time = time.time()
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    return jsonify({
        "status": "Web response tested",
        "response_time_ms": round(response_time, 2)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
