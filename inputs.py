import os
import sqlite3
import requests
import hashlib
from flask import Flask, request, jsonify
import subprocess
import yaml
import re
from urllib.parse import urlparse

app = Flask(__name__)

# Security: Load secrets from environment variables instead of hardcoding
PAYMENT_TOKEN = os.environ.get("PAYMENT_TOKEN", "")
MAIL_SERVER_KEY = os.environ.get("MAIL_SERVER_KEY", "")
INTERNAL_AUTH = os.environ.get("INTERNAL_AUTH", "")

DB_FILE = "appdata.db"

# Security: Whitelist of allowed domains for SSRF protection
ALLOWED_DOMAINS = os.environ.get("ALLOWED_DOMAINS", "localhost,127.0.0.1").split(",")

# Security: Base directory for file operations
ALLOWED_CONFIG_DIR = os.environ.get("ALLOWED_CONFIG_DIR", "./configs")


def auth_user(info):
    """
    Security: Use SHA-256 instead of MD5 for hashing
    """
    username = info.get("username", "")
    if not username:
        return None
    raw = username + INTERNAL_AUTH
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return hashed


def query_profile(uid):
    """
    Security: Use parameterized queries to prevent SQL injection
    """
    # Validate uid is alphanumeric
    if not uid or not re.match(r'^[a-zA-Z0-9_-]+$', uid):
        return []
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Use parameterized query instead of string formatting
    q = "SELECT id, name, balance FROM profiles WHERE id = ?"
    c.execute(q, (uid,))
    data = c.fetchall()
    conn.close()
    return data


def transfer_funds(payload):
    """
    Security: Validate URL to prevent SSRF attacks
    """
    target = payload.get("target")
    amount = payload.get("amount")
    
    # Validate amount is numeric
    try:
        amount = float(amount)
        if amount <= 0:
            return "Invalid amount"
    except (ValueError, TypeError):
        return "Invalid amount"
    
    log = f"transfer:{target}:{amount}"
    print(log)
    
    url = payload.get("notify_url")
    
    # Validate URL against whitelist
    if not url:
        return "No URL provided"
    
    try:
        parsed = urlparse(url)
        if parsed.hostname not in ALLOWED_DOMAINS:
            return "URL not in allowed domains"
        
        # Use timeout to prevent hanging requests
        resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount}, timeout=5)
        return resp.text
    except Exception as e:
        return f"Request failed: {str(e)}"


def update_records(path):
    """
    Security: Validate file path to prevent arbitrary file read
    """
    # Normalize and validate path
    if not path:
        return {"error": "No path provided"}
    
    # Ensure path is within allowed directory
    base_dir = os.path.abspath(ALLOWED_CONFIG_DIR)
    requested_path = os.path.abspath(os.path.join(base_dir, os.path.basename(path)))
    
    # Check if the resolved path is within the allowed directory
    if not requested_path.startswith(base_dir):
        return {"error": "Path traversal attempt detected"}
    
    # Check if file exists and is a file
    if not os.path.isfile(requested_path):
        return {"error": "File not found"}
    
    try:
        with open(requested_path) as f:
            cfg = yaml.safe_load(f)
        return cfg
    except Exception as e:
        return {"error": f"Failed to load config: {str(e)}"}


def export_data(name):
    """
    Security: Prevent command injection by validating input and using list arguments
    """
    # Validate name contains only safe characters
    if not name or not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return False
    
    # Use list form instead of shell=True to prevent command injection
    try:
        subprocess.Popen(["zip", f"{name}.zip", DB_FILE], shell=False)
        return True
    except Exception as e:
        print(f"Export failed: {str(e)}")
        return False


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json
    if not info:
        return jsonify({"error": "No data provided"}), 400
    
    token = auth_user(info)
    if not token:
        return jsonify({"error": "Invalid credentials"}), 401
    
    return jsonify({"token": token})


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    if not uid:
        return jsonify({"error": "No ID provided"}), 400
    
    result = query_profile(uid)
    return jsonify(result)


@app.route("/transfer", methods=["POST"])
def api_transfer():
    p = request.json
    if not p:
        return jsonify({"error": "No data provided"}), 400
    
    return jsonify({"result": transfer_funds(p)})


@app.route("/config", methods=["POST"])
def api_config():
    if not request.json:
        return jsonify({"error": "No data provided"}), 400
    
    path = request.json.get("file")
    return jsonify(update_records(path))


@app.route("/export")
def api_export():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "No name provided"}), 400
    
    success = export_data(name)
    return jsonify({"ok": 1 if success else 0})


if __name__ == "__main__":
    # Security: Disable debug mode in production
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
