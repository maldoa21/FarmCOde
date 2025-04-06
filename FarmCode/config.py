import threading


# Sensor modbus port for temperature and humidity readings.
MODBUS_PORT = "/dev/ttyUSB0"  # TODO: Change this to your actual modbus port

# GPIO pins on or off for motor control. True means motor (GPIO) control is active.
motorControl = True

# Shutter GPIO mapping: only output pins are now used.
SLUG_SHUTTER_PINS = {
    "open": {"out_pin": 3},  # 5
    "close": {"out_pin": 17},  # 11
}
SLUG_SIDEWALL_PINS = {
    "open": {"out_pin": 27},  # 13
    "close": {"out_pin": 22},  # 15
}

LED_PIN = 5                   # LED for pre-/post-operation indication
MOTOR_RUNTIME = 15            # seconds the motor must stay HIGH exactly

# Database and log configuration.
DB_FILE = "shutters_control.db"
LOG_FILE = "logged_data.json"

# Global stop event – used by threads for graceful shutdown.
stop_event = threading.Event()

# Pi GPIO UART pins.
"""
RS485 UART transmit: GPIO 14 (TXD) - Pin 8
RS485 UART receive: GPIO 15 (RXD) - Pin 10
Uses 3.3V logic level
Turn on UART on Raspberry Pi using `sudo raspi-config` and enable the serial interface.
RSE (TX/RX control) is auto by default but high for TX and low for RX.
"""
