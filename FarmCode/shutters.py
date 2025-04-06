import threading
import time
from management.logger import log_event
from DbUI.database import update_shutter_status
from gpio.gpio_control import gpio_lines, motor_started, motor_finished
from management.config import MOTOR_RUNTIME, SLUG_SHUTTER_PINS, SLUG_SIDEWALL_PINS, motorControl

operation_threads = {}          # device -> Thread
operation_cancel_flags = {}     # device -> threading.Event
operation_threads_lock = threading.Lock()
operation_intended_actions = {} # device -> intended action (open/close)

def operate_shutter(device: str, action: str):
    mapping = None
    if device == "Slug Shutter":
        mapping = SLUG_SHUTTER_PINS
    elif device == "Slug Sidewall":
        mapping = SLUG_SIDEWALL_PINS
    if not mapping or action not in mapping:
        log_event(f"ERROR: Invalid device '{device}' or action '{action}'.")
        return

    # Create a cancellation flag and save it for the device.
    cancel_flag = threading.Event()
    with operation_threads_lock:
        # Set any existing flag to cancel the current operation.
        if device in operation_cancel_flags:
            operation_cancel_flags[device].set()
        operation_cancel_flags[device] = cancel_flag
        operation_intended_actions[device] = action

    # Simulation branch: when motorControl is enabled.
    if not motorControl:
        log_event(f"SIMULATION: {action.upper()} operation initiated for {device}.")
        motor_started()
        try:
            time.sleep(MOTOR_RUNTIME)
            # If cancellation was requested, skip updating the status so that "live" remains.
            if cancel_flag.is_set():
                log_event(f"SIMULATION: Operation for {device} was cancelled; skipping final update.")
                return
            final_state = "closed" if action == "close" else action
            update_shutter_status(device, final_state)
            log_event(f"SIMULATION: {action.upper()} operation completed for {device}.")
        finally:
            motor_finished()
        return

    # Normal operation below if motorControl is False. 
    
    # TODO: Add logic here for "automatic" operation if needed then return.
    # 1. Check if action is "automatic".
    # 2. If so, call a new function (e.g., `determine_automatic_action(device)`) to decide whether to open or close.
    #    - Connect and turn on sensor protocols (e.g., I2C, SPI, 1 wire) to read data.
    #    - This function should read sensor data (temperature, humidity, etc.). You'll need to import modules for sensor access.
    #    - Based on the sensor data and predefined thresholds, decide on the appropriate action ("open" or "close").
    # 3. Call `operate_shutter` recursively with the determined action.
    #    - Example: `operate_shutter(device, determined_action)`
    # 4. Ensure proper error handling and logging within the new function.
    # 5. Consider how long motors should be moved and if there is feedback from the motor (e.g., limit switches).

    # For Manual GPIO control.
    pins = mapping[action]
    out_pin = pins["out_pin"]
    out_line = gpio_lines.get(out_pin)
    if not out_line:
        log_event(f"ERROR: Could not access output line for {device}.")
        return

    def shutter_thread():
        try:
            log_event(f"START: {action.upper()} operation initiated for {device}.")
            motor_started()  # TODO: Add here for automatic operation.
            out_line.set_value(1)
            log_event(f"{device}: Motor (pin {out_pin}) set to HIGH for {action.upper()}.")

            # Use cancel_flag.wait() to replace time.sleep(MOTOR_RUNTIME)
            # This will return True if cancel_flag is set within the timeout.
            if cancel_flag.wait(MOTOR_RUNTIME):
                log_event(f"Operation for {device} was cancelled; stopping motor immediately.")
                out_line.set_value(0)
                return

            out_line.set_value(0)
            log_event(f"{device}: Motor (pin {out_pin}) set to LOW, ending {action.upper()} operation.")

            if cancel_flag.is_set():
                log_event(f"Operation for {device} was cancelled; skipping final update.")
                return

            final_state = "closed" if action == "close" else action
            update_shutter_status(device, final_state)
            log_event(f"COMPLETE: {action.upper()} operation completed for {device}.")
        except Exception as ex:
            log_event(f"ERROR: Exception in shutter operation for {device} during {action}: {ex}")
        finally:
            motor_finished()  # TODO: Add here for automatic operation.
            with operation_threads_lock:
                if device in operation_intended_actions:
                    del operation_intended_actions[device]
                if device in operation_cancel_flags and operation_cancel_flags[device] == cancel_flag:
                    del operation_cancel_flags[device]
    thread = threading.Thread(target=shutter_thread, daemon=True)
    with operation_threads_lock:
        operation_threads[device] = thread
    thread.start()

def cancel_shutter_operation(device: str):
    with operation_threads_lock:
        if device in operation_cancel_flags:
            operation_cancel_flags[device].set()
            log_event(f"Cancellation signal sent for {device}.")
        else:
            log_event(f"No operation to cancel for {device}.")
