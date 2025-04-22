from flask import Blueprint, render_template_string

shutter_data = Blueprint("shutter_data", __name__)

@shutter_data.route("/shutter-data")
def view_full_log():
    # FAKE SAMPLE LOG DATA FOR UI DEMO
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

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Full Shutter Log</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 20px; background-color: #f9f9f9; }
            table { margin: auto; border-collapse: collapse; width: 80%; background: white; }
            th, td { padding: 10px; border: 1px solid #ccc; }
            th { background-color: #007BFF; color: white; }
        </style>
    </head>
    <body>
        <h1>Full Shutter Log</h1>
        <table>
            <tr><th>Timestamp</th><th>Event</th></tr>
            {% for log in logs %}
            <tr><td>{{ log[0] }}</td><td>{{ log[1] }}</td></tr>
            {% endfor %}
        </table>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """
    return render_template_string(html, logs=logs)
