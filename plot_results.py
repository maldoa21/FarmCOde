import json
import matplotlib.pyplot as plt

# Function to read results from a JSON log file
def load_results(filename):
    results = []
    try:
        with open(filename, "r") as file:
            for line in file:
                results.append(json.loads(line.strip()))
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return results

# Load data
shutter_results = load_results("shutter_results.json")
web_results = load_results("web_results.json")

# Extract data
shutter_times = [entry["average_toggle_time_ms"] for entry in shutter_results]
web_times = [entry["average_response_time_ms"] for entry in web_results]

# Plot Shutter Toggle Time
plt.figure(figsize=(10, 5))
plt.plot(shutter_times, label="Shutter Toggle Time (ms)", marker="o", linestyle="-")
plt.axhline(y=1000, color="r", linestyle="--", label="1-second Limit")
plt.xlabel("Test Run")
plt.ylabel("Time (ms)")
plt.title("Shutter Toggle Time Over Test Runs")
plt.legend()
plt.grid()
plt.savefig("shutter_toggle_time.png")  # Save the figure
plt.show()

# Plot Web Response Time
plt.figure(figsize=(10, 5))
plt.plot(web_times, label="Web Response Time (ms)", marker="s", linestyle="-", color="g")
plt.axhline(y=500, color="r", linestyle="--", label="500ms Limit")
plt.xlabel("Test Run")
plt.ylabel("Time (ms)")
plt.title("Web Response Time Over Test Runs")
plt.legend()
plt.grid()
plt.savefig("web_response_time.png")
plt.show()
