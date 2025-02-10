import requests
import time

# API Endpoints
URL_TOGGLE = "http://127.0.0.1:5000/toggle_shutter"
URL_STATUS = "http://127.0.0.1:5000/status"

# Test Shutter Toggle Time
def test_shutter_toggle():
    results = []
    for i in range(500):
        start_time = time.time()
        try:
            response = requests.get(URL_TOGGLE).json()
            toggle_time = response.get("toggle_time_ms", -1)
            results.append(toggle_time)

            print(f"Test {i+1}: Shutter Toggle Time = {toggle_time:.2f} ms")
        except requests.exceptions.RequestException as e:
            print(f"Test {i+1}: FAILED - {e}")
        
        time.sleep(0.1)  # Small delay to avoid overload

    avg_time = sum(results) / len(results) if results else 0
    print(f"\nAverage Shutter Toggle Time: {avg_time:.2f} ms")
    return results

# Test Web Response Time
def test_web_response():
    results = []
    success_count = 0

    for i in range(100):
        start_time = time.time()
        try:
            response = requests.get(URL_STATUS)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms

            if response.status_code == 200:
                success_count += 1

            results.append(response_time)
            print(f"Test {i+1}: Web Response Time = {response_time:.2f} ms")

        except requests.exceptions.RequestException as e:
            print(f"Test {i+1}: FAILED - {e}")
        
        time.sleep(0.1)

    avg_time = sum(results) / len(results) if results else 0
    success_rate = (success_count / 100) * 100
    print(f"\nSuccess Rate: {success_rate:.2f}%")
    print(f"Average Web Response Time: {avg_time:.2f} ms")
    return results

if __name__ == "__main__":
    print("Starting Shutter Toggle Test...")
    toggle_results = test_shutter_toggle()

    print("\nStarting Web Response Time Test...")
    web_results = test_web_response()
