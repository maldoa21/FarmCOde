from flask import Blueprint, request, redirect, url_for, render_template_string, has_request_context

auth = Blueprint("auth", __name__, url_prefix="/auth")

# Plaintext password
PLAIN_PASSWORD = "harvestking"

# Login HTML form
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

# Login route: redirects to /home with ?access=true if correct
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

# Only intercept real HTTP requests
@auth.before_app_request
def require_password_every_time():
    if not has_request_context():
        return  # Don't block sensor/background threads

    allowed_paths = [
        "/auth/login",
        "/static",
        "/favicon.ico"
    ]

    path = request.path
    if any(path.startswith(p) for p in allowed_paths):
        return

    if request.endpoint == "auth.login":
        return

    if request.args.get("access") != "true":
        return redirect(url_for("auth.login"))
