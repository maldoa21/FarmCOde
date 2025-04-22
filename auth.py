from flask import Blueprint, request, redirect, url_for, render_template_string, has_request_context
import threading

auth = Blueprint("auth", __name__, url_prefix="/auth")

# Hardcoded plaintext password
PLAIN_PASSWORD = "harvestking"

# Login form template
login_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Shutter Control</title>
    <style>
        body { font-family: Arial; background: #f4f4f4; text-align: center; padding-top: 100px; }
        form { background: white; display: inline-block; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px #ccc; }
        input[type=password] { padding: 10px; width: 80%; margin: 10px 0; }
        input[type=submit] { padding: 10px 20px; background: #007BFF; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <form method="POST">
        <h2>Enter Access Code</h2>
        <input type="password" name="password" placeholder="Password" required><br>
        <input type="submit" value="Enter">
        {% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
    </form>
</body>
</html>
"""

# Route: GET/POST login form
@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == PLAIN_PASSWORD:
            return redirect(url_for("index", access="true"))
        else:
            error = "Incorrect password"
    return render_template_string(login_template, error=error)

# Global password check, safe for GPIO
@auth.before_app_request
def require_password_per_request():
    # Only run this logic in real HTTP request contexts
    if not has_request_context():
        print(f"[AUTH] Skipped password check (not an HTTP request). Thread: {threading.current_thread().name}")
        return

    # Allow the login route and static resources
    path = request.path
    if (
        path.startswith("/auth/login")
        or path.startswith("/static")
        or path == "/favicon.ico"
    ):
        return

    if request.endpoint == "auth.login":
        return

    # Require ?access=true for other pages
    if request.args.get("access") != "true":
        print(f"[AUTH] Blocking access to {path}. Missing ?access=true")
        return redirect(url_for("auth.login"))
