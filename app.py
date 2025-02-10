from flask import Flask, jsonify
import time

# Create Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "Raspberry Pi Web Test Server is Running", 200

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
