import json
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

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
    data = request.get_json()
    users = load_users()
    # Use host+timestamp as unique key to avoid overwriting
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

@app.route("/")
def index():
    return (
        "OWL Backend API<br>"
        "/api/register_user (POST: register)<br>"
        "/api/app_status (GET: global enable/disable)<br>"
        "/api/user_count (GET: total registered users)"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)