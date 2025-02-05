from flask import Flask, jsonify, request
import RPi.GPIO as GPIO
import time

# Flask app initialization
app = Flask(__name__)

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setwarnings(False)

# Define test GPIO pins
TEST_PINS = [17, 18, 22, 23]

# Set up pins as output
for pin in TEST_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Initialize pins to LOW

@app.route("/")
def home():
    return jsonify({"message": "Raspberry Pi GPIO Test Server is Running!"})

@app.route("/toggle/<int:pin>", methods=["POST"])
def toggle_pin(pin):
    if pin not in TEST_PINS:
        return jsonify({"error": f"Invalid GPIO pin {pin}"}), 400

    # Toggle the pin
    current_state = GPIO.input(pin)
    new_state = GPIO.LOW if current_state == GPIO.HIGH else GPIO.HIGH
    GPIO.output(pin, new_state)

    return jsonify({
        "pin": pin,
        "previous_state": "HIGH" if current_state else "LOW",
        "new_state": "HIGH" if new_state else "LOW"
    })

@app.route("/status/<int:pin>", methods=["GET"])
def pin_status(pin):
    if pin not in TEST_PINS:
        return jsonify({"error": f"Invalid GPIO pin {pin}"}), 400

    state = GPIO.input(pin)
    return jsonify({"pin": pin, "state": "HIGH" if state else "LOW"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
