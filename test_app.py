import unittest
import requests
import time

# Replace this with your Raspberry Pi’s IP address
PI_IP = "192.168.1.131"  
BASE_URL = f"http://{PI_IP}:5000"

# Define GPIO pins to test
TEST_PINS = [17, 18, 22, 23]

class TestRaspberryPiGPIO(unittest.TestCase):

    def test_toggle_pins(self):
        """Toggle each pin 500 times and log the response time."""
        log_data = []

        for pin in TEST_PINS:
            for i in range(500):
                start_time = time.time()
                response = requests.post(f"{BASE_URL}/toggle/{pin}")
                end_time = time.time()
                duration = round((end_time - start_time) * 1000, 2)  # Convert to ms

                log_data.append({"pin": pin, "test_number": i+1, "response_time_ms": duration})
                self.assertEqual(response.status_code, 200)

        # Save log results
        with open("gpio_toggle_test_log.csv", "w") as f:
            f.write("Pin,Test Number,Response Time (ms)\n")
            for log in log_data:
                f.write(f"{log['pin']},{log['test_number']},{log['response_time_ms']}\n")

    def test_pin_status(self):
        """Check the status of each pin after toggling."""
        for pin in TEST_PINS:
            response = requests.get(f"{BASE_URL}/status/{pin}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(response.json()["state"], ["HIGH", "LOW"])

    def test_invalid_pin(self):
        """Ensure the API returns an error for invalid pins."""
        response = requests.post(f"{BASE_URL}/toggle/999")  # Invalid pin
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
