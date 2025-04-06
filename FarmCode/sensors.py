# Run 'lsusb' to get the USB device ID for the sensors
# or run 'dmesg | grep -i tty' to find the connected USB device.
# This is typically something like '/dev/ttyUSB0' or '/dev/ttyACM0'.

# Run pip install pymodbus

# This script reads temperature and humidity data from a Modbus RTU device connected via USB.
# It uses the pymodbus library to communicate with the device.
import asyncio
import json
import os
from pymodbus.client import AsyncModbusSerialClient as ModbusClient  # type: ignore
from pymodbus.exceptions import ModbusException  # type: ignore
from management.logger import log_event
from management.config import stop_event, MODBUS_PORT

# Try to determine the correct port automatically or use environment variable
def get_modbus_port():
    return MODBUS_PORT
    
    
    # Check if port is specified in an environment variable.
    if 'MODBUS_PORT' in os.environ:
        return os.environ['MODBUS_PORT']
    
    # First try the Pi's primary UART.
    if os.path.exists('/dev/serial0'):
        return '/dev/serial0'
    
    # Next, check for common USB ports.
    for port in ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyUSB1']:
        if os.path.exists(port):
            return port

async def read_sensor_data():
    """
    Read temperature and humidity data from the Modbus device.
    
    Returns:
        dict: A dictionary with temperature and humidity values,
              or an error message if something went wrong.
    """
    port = get_modbus_port()
    client = ModbusClient(
        port=port,
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=1
    )
    
    try:
        # Establish connection using an async context manager
        async with client as connected_client:
            if not connected_client.connected:
                log_event(f"Failed to connect to Modbus device on {port}")
                return {"error": f"Unable to connect to the Modbus device on {port}"}
                
            # Read 2 holding registers (function code 03) starting at address 0
            # Device (slave) address is 1
            result = await connected_client.read_holding_registers(address=0, count=2, unit=1)
            
            if result.isError():
                log_event(f"Error reading Modbus registers: {result}")
                return {"error": f"Error reading registers: {result}"}
                
            registers = result.registers
            if len(registers) >= 2:
                # Convert raw values by dividing by 100
                temperature = registers[0] / 100.0
                humidity = registers[1] / 100.0
                return {
                    "temperature": temperature,
                    "humidity": humidity
                }
            else:
                log_event(f"Unexpected register count: {len(registers)}")
                return {"error": "Unexpected register count received"}
                
    except ModbusException as e:
        log_event(f"Modbus Exception: {e}")
        return {"error": f"Modbus Exception: {e}"}
    except Exception as e:
        log_event(f"Unexpected error reading sensor data: {e}")
        return {"error": f"Unexpected error: {e}"}

async def monitor_sensors():
    """
    Continuously monitor sensors and print readings.
    Checks for the stop_event flag for graceful shutdown.
    """
    log_event("Starting continuous sensor monitoring...")
    try:
        while not stop_event.is_set():
            data = await read_sensor_data()
            if "error" in data:
                print(f"Error: {data['error']}")
            else:
                temp = data["temperature"]
                humidity = data["humidity"]
                print(f"Temperature: {temp:.2f}°C, Humidity: {humidity:.2f}%")
            
            # Instead of awaiting on stop_event.wait(), simply sleep for 3 seconds.
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        log_event("Sensor monitoring task cancelled")
    finally:
        log_event("Sensor monitoring stopped")

# Run this script via the asyncio event loop
if __name__ == "__main__":
    # For demonstration purposes - run continuous monitoring
    asyncio.run(monitor_sensors())