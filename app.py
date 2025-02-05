from flask import Flask, jsonify, request
from gpiozero import LED
from time import sleep

# Initialize Flask app
app = Flask(__name__)

# GPIO setup using gpiozero
# Define the GPIO pins to be controlled
PINS = {
    17: LED(17),
    18: LED(18),
    22: LED(22),
    23: LED(23)
}

# Home route
@app.route("/")
def home():
    return jsonify({"message": "Raspberry Pi GPIO Control API is Running!"})

# Route to toggle a GPIO pin
@app.route("/toggle/<int:pin>", methods=["POST"])
def toggle_pin(pin):
    if pin not in PINS:
        return jsonify({"error": f"Invalid GPIO pin {pin}"}), 400

    pin_obj = PINS[pin]
    pin_obj.toggle()  # Toggle the pin state

    state = "HIGH" if pin_obj.is_lit else "LOW"
    return jsonify({
        "pin": pin,
        "new_state": state
    })

# Route to get the status of a GPIO pin
@app.route("/status/<int:pin>", methods=["GET"])
def pin_status(pin):
    if pin not in PINS:
        return jsonify({"error": f"Invalid GPIO pin {pin}"}), 400

    pin_obj = PINS[pin]
    state = "HIGH" if pin_obj.is_lit else "LOW"
    return jsonify({
        "pin": pin,
        "state": state
    })

# Route to turn all pins OFF
@app.route("/reset", methods=["POST"])
def reset_pins():
    for pin_obj in PINS.values():
        pin_obj.off()

    return jsonify({"message": "All GPIO pins have been turned OFF."})

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
