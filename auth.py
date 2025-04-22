from flask import Blueprint, request, redirect, url_for, render_template_string, session, has_request_context
from functools import wraps

auth = Blueprint("auth", __name__, url_prefix="/auth")

# Always-required plaintext password
PLAIN_PASSWORD = "harvestking"

# Login template
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

# Login route
@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == PLAIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            error = "Incorrect password"
    return render_template_string(login_template, error=error)

# Logout route
@auth.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("auth.login"))

# Decorator to protect routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# Global request filter
@auth.before_app_request
def always_require_password():
    if not has_request_context():
        return  # avoid interfering with background threads (like GPIO/sensors)

    # Allow static, login, favicon, and logout routes
    allowed_paths = [
        "/auth/login",
        "/auth/logout",
        "/static",
        "/favicon.ico"
    ]
    if any(request.path.startswith(p) for p in allowed_paths):
        return

    # If not logged in, redirect
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))
