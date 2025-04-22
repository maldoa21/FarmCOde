from flask import Blueprint, render_template_string

shutter_data = Blueprint("shutter_data", __name__)

@shutter_data.route("/shutter-data")
def view_full_log():
    # Sample shutter log data
    logs = [
        ("2025-04-08 07:30 AM", "Slug Shutter opened manually"),
        ("2025-04-08 08:15 AM", "Slug Sidewall closed automatically"),
        ("2025-04-08 09:05 AM", "Slug Shutter set to automatic mode"),
        ("2025-04-08 10:22 AM", "Slug Sidewall opened manually"),
        ("2025-04-08 11:45 AM", "Slug Shutter closed manually"),
        ("2025-04-08 01:03 PM", "Slug Sidewall set to automatic mode"),
        ("2025-04-08 03:30 PM", "Slug Shutter opened automatically"),
        ("2025-04-08 04:10 PM", "Slug Sidewall closed manually"),
        ("2025-04-08 05:00 PM", "Slug Shutter set to automatic mode")
    ]

    # Sample temperature sensor log data
    temperature_logs = [
        ("2025-04-08 07:00 AM", "72.5 °F"),
        ("2025-04-08 08:00 AM", "74.3 °F"),
        ("2025-04-08 09:00 AM", "75.8 °F"),
        ("2025-04-08 10:00 AM", "77.1 °F"),
        ("2025-04-08 11:00 AM", "78.4 °F"),
        ("2025-04-08 12:00 PM", "79.9 °F"),
        ("2025-04-08 01:00 PM", "81.2 °F"),
        ("2025-04-08 02:00 PM", "80.3 °F"),
        ("2025-04-08 03:00 PM", "78.7 °F")
    ]

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Full Shutter & Temperature Log</title>
        <style>
            body { font-family: Arial; padding: 20px; background-color: #f9f9f9; }
            h1, h2 { text-align: center; color: #333; }
            table { width: 90%; margin: 20px auto; border-collapse: collapse; background: white; }
            th, td { padding: 10px; border: 1px solid #ccc; text-align: center; }
            th { background-color: #007BFF; color: white; }
            a { text-align: center; display: block; margin-top: 20px; color: #007BFF; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>System Log Overview</h1>

        <h2>Shutter Activity Log</h2>
        <table>
            <tr><th>Timestamp</th><th>Event</th></tr>
            {% for log in logs %}
            <tr><td>{{ log[0] }}</td><td>{{ log[1] }}</td></tr>
            {% endfor %}
        </table>

        <h2>Temperature Sensor Readings</h2>
        <table>
            <tr><th>Timestamp</th><th>Temperature</th></tr>
            {% for temp in temperature_logs %}
            <tr><td>{{ temp[0] }}</td><td>{{ temp[1] }}</td></tr>
            {% endfor %}
        </table>

        <a href="/">← Back to Home</a>
    </body>
    </html>
    """

    return render_template_string(html, logs=logs, temperature_logs=temperature_logs)
