import json
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os

app = Flask(__name__, template_folder="../templates")

USERS_FILE = "users.json"
APP_ENABLED = True  # Change to False to globally disable opi

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

@app.route("/api/register_user", methods=["POST"])
def register_user():
    if request.method != "POST":
        return jsonify({"error": "Method Not Allowed"}), 405

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    users = load_users()
    key = f"{data.get('host', 'unknown')}_{data.get('timestamp', datetime.utcnow().isoformat())}"
    users[key] = data
    save_users(users)
    return jsonify({"ok": True, "user_count": len(users)})

@app.route("/api/app_status", methods=["GET"])
def app_status():
    return jsonify({"enabled": APP_ENABLED})

@app.route("/api/user_count", methods=["GET"])
def user_count():
    users = load_users()
    return jsonify({"user_count": len(users)})

@app.route("/users", methods=["GET"])
def show_users():
    users = load_users()
    return render_template("users.html", users=users.values(), count=len(users))

@app.route("/")
def index():
    return (
        "<h2>🦉 OWL Backend API</h2>"
        "<ul>"
        "<li><strong>POST</strong> /api/register_user — Register user</li>"
        "<li><strong>GET</strong> /api/app_status — Check global enable/disable</li>"
        "<li><strong>GET</strong> /api/user_count — Total registered users</li>"
        "<li><strong>GET</strong> /users — View registered users in HTML</li>"
        "</ul>"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
