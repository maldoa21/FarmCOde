from flask import Blueprint, render_template_string
from DbUI.database import init_db

shutter_data = Blueprint("shutter_data", __name__)

@shutter_data.route("/shutter-data")
def view_full_log():
    logs = get_all_logs()
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Full Shutter Log</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 20px; }
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
