import os
import sqlite3
import requests
import bcrypt
from flask import Flask, request, jsonify
import subprocess
import yaml
import logging
from urllib.parse import urlparse
import ipaddress
import zipfile

app = Flask(__name__)

# Secrets loaded from environment variables
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN', '')
MAIL_SERVER_KEY = os.getenv('MAIL_SERVER_KEY', '')
INTERNAL_AUTH = os.getenv('INTERNAL_AUTH', '')

DB_FILE = "appdata.db"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def auth_user(info):
    """Hash username using bcrypt for secure authentication."""
    username = info.get("username", "")
    # In a real application, use proper password hashing for passwords, not usernames
    hashed = bcrypt.hashpw(username.encode(), bcrypt.gensalt()).decode()
    return hashed


def query_profile(uid):
    """Query profile using parameterized queries to prevent SQL injection."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Use parameterized query instead of string concatenation
    q = "SELECT id,name,balance FROM profiles WHERE id = ?"
    c.execute(q, (uid,))
    data = c.fetchall()
    conn.close()
    return data


def is_safe_url(url):
    """Validate URL to prevent SSRF attacks."""
    try:
        parsed = urlparse(url)
        # Only allow HTTP and HTTPS
        if parsed.scheme not in ('http', 'https'):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Check for private IP ranges
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback:
                return False
        except ValueError:
            # Not an IP address, check domain
            pass
        return True
    except Exception:
        return False


def transfer_funds(payload):
    """Transfer funds with validation."""
    target = payload.get("target")
    amount = payload.get("amount")
    # Use proper logging instead of print
    logger.info(f"transfer:{target}:{amount}")
    
    url = payload.get("notify_url")
    # Validate URL before making request
    if not is_safe_url(url):
        raise ValueError("Invalid notification URL")
    
    # Removed hardcoded token exposure - should use environment variable
    resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount})
    return resp.text


def update_records(path):
    """Load records with path traversal protection."""
    # Validate and sanitize file path
    base_dir = os.path.abspath('config')
    full_path = os.path.abspath(path)
    
    # Ensure path stays within base directory
    if not full_path.startswith(base_dir):
        raise ValueError("Invalid path - access denied")
    
    # Check if file exists
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(full_path) as f:
        cfg = yaml.safe_load(f)
    return cfg


def validate_export_name(name):
    """Validate export name to prevent command injection."""
    if not isinstance(name, str):
        raise ValueError("Name must be a string")
    if len(name) > 50:
        raise ValueError("Name too long")
    if '/' in name or '\\' in name or '..' in name:
        raise ValueError("Invalid characters in name")
    return name


def export_data(name):
    """Export data using safe zipfile API instead of shell command."""
    name = validate_export_name(name)
    try:
        with zipfile.ZipFile(f'{name}.zip', 'w') as zf:
            zf.write(DB_FILE)
        return True
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        return False


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json
    try:
        return jsonify({"token": auth_user(info)})
    except Exception as e:
        return jsonify({"error": "Authentication failed"}), 400


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    if not uid:
        return jsonify({"error": "Missing id parameter"}), 400
    try:
        return jsonify(query_profile(uid))
    except Exception as e:
        return jsonify({"error": "Profile query failed"}), 400


@app.route("/transfer", methods=["POST"])
def api_transfer():
    p = request.json
    if not p:
        return jsonify({"error": "Invalid request"}), 400
    try:
        return jsonify({"result": transfer_funds(p)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Transfer failed"}), 500


@app.route("/config", methods=["POST"])
def api_config():
    path = request.json.get("file") if request.json else None
    if not path:
        return jsonify({"error": "Missing file parameter"}), 400
    try:
        return jsonify(update_records(path))
    except (ValueError, FileNotFoundError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Config update failed"}), 500


@app.route("/export")
def api_export():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing name parameter"}), 400
    try:
        if export_data(name):
            return jsonify({"ok": 1})
        else:
            return jsonify({"error": "Export failed"}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Export failed"}), 500


if __name__ == "__main__":
    # Debug mode controlled by environment variable, defaults to False for security
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
