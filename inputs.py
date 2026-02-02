import os
import sqlite3
import requests
import hashlib
import hmac
import logging
import zipfile
from urllib.parse import urlparse
from flask import Flask, request, jsonify, abort
import yaml

app = Flask(__name__)

# Secrets must come from environment variables in production
PAYMENT_TOKEN = os.environ.get("PAYMENT_TOKEN")
MAIL_SERVER_KEY = os.environ.get("MAIL_SERVER_KEY")
INTERNAL_AUTH = os.environ.get("INTERNAL_AUTH")

# Configuration
DB_FILE = os.environ.get("DB_FILE", "appdata.db")
CONFIG_DIR = os.environ.get("CONFIG_DIR", ".")
ALLOWED_NOTIFY_HOSTS = os.environ.get("ALLOWED_NOTIFY_HOSTS", "").split(",") if os.environ.get("ALLOWED_NOTIFY_HOSTS") else []
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def auth_user(info):
    username = info.get("username")
    if not username:
        raise ValueError("username required")
    if not INTERNAL_AUTH:
        raise RuntimeError("INTERNAL_AUTH is not configured")
    # Use HMAC-SHA256 with secret from environment for token generation
    token = hmac.new(INTERNAL_AUTH.encode(), username.encode(), hashlib.sha256).hexdigest()
    return token


def query_profile(uid):
    # Validate uid is integer to prevent SQL injection
    try:
        uid_int = int(uid)
    except (TypeError, ValueError):
        raise ValueError("invalid uid")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id,name,balance FROM profiles WHERE id = ?", (uid_int,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def transfer_funds(payload):
    target = payload.get("target")
    amount = payload.get("amount")
    url = payload.get("notify_url")

    # Validate inputs
    if not target or not url or amount is None:
        raise ValueError("missing transfer parameters")
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValueError("amount must be positive")
    except (TypeError, ValueError):
        raise ValueError("invalid amount")

    # Prevent SSRF: allow only https and optional whitelist
    parsed = urlparse(url)
    if parsed.scheme not in ("https",):
        raise ValueError("notify_url must use https")
    if ALLOWED_NOTIFY_HOSTS and parsed.hostname not in ALLOWED_NOTIFY_HOSTS:
        raise ValueError("notify_url hostname not allowed")

    logger.info("transfer:%s:%s", target, amount)

    if not PAYMENT_TOKEN:
        raise RuntimeError("PAYMENT_TOKEN is not configured")

    resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount_float}, timeout=5)
    return resp.text


def update_records(path):
    # Only allow loading configs from CONFIG_DIR
    if not path:
        raise ValueError("file path required")
    full = os.path.realpath(os.path.join(CONFIG_DIR, path))
    if not full.startswith(os.path.realpath(CONFIG_DIR)):
        raise ValueError("access to path not allowed")
    with open(full) as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name):
    # Validate simple filename and create zip archive safely
    if not name or os.path.sep in name or name.startswith('.'):
        raise ValueError("invalid name")
    archive_name = f"{name}.zip"
    with zipfile.ZipFile(archive_name, 'w') as z:
        z.write(DB_FILE)
    return True


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json
    return jsonify({"token": auth_user(info)})


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    return jsonify(query_profile(uid))


def require_admin(fn):
    def wrapper(*args, **kwargs):
        key = request.headers.get('X-API-KEY')
        if not ADMIN_API_KEY or key != ADMIN_API_KEY:
            abort(403)
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


@app.route("/transfer", methods=["POST"])
@require_admin
def api_transfer():
    p = request.json
    return jsonify({"result": transfer_funds(p)})


def api_config():
@app.route("/config", methods=["POST"])
@require_admin
def api_config():
    path = request.json.get("file")
    return jsonify(update_records(path))


@app.route("/export")
@require_admin
def api_export():
    name = request.args.get("name")
    export_data(name)
    return jsonify({"ok": 1})


if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
