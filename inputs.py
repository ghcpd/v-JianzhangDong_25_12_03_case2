import os
import sqlite3
import requests
import hashlib
import hmac
import logging
from flask import Flask, request, jsonify, abort
import zipfile
import yaml
from urllib.parse import urlparse

app = Flask(__name__)

# Secrets must come from environment variables in production
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")
MAIL_SERVER_KEY = os.getenv("MAIL_SERVER_KEY", "")
INTERNAL_AUTH_KEY = os.getenv("INTERNAL_AUTH_KEY", "")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

# Ensure a safe data directory
DATA_DIR = os.getenv("DATA_DIR", "./data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, os.getenv("DB_FILE", "appdata.db"))

# Configs and exports should be confined to controlled directories
CONFIG_DIR = os.path.join(DATA_DIR, "configs")
EXPORT_DIR = os.path.join(DATA_DIR, "exports")
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

ALLOWED_NOTIFY_DOMAINS = [d.strip() for d in os.getenv("ALLOWED_NOTIFY_DOMAINS", "").split(",") if d.strip()]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def auth_user(info: dict) -> str:
    """Create a HMAC-SHA256 token for the provided username using a secret key.

    This uses HMAC with SHA-256 instead of MD5 to avoid weak hashing.
    INTERNAL_AUTH_KEY must be set via environment in production.
    """
    username = info.get("username", "")
    if not INTERNAL_AUTH_KEY:
        # Avoid generating predictable tokens in environments without a key
        raise RuntimeError("INTERNAL_AUTH_KEY is required for creating auth tokens")
    mac = hmac.new(INTERNAL_AUTH_KEY.encode(), username.encode(), hashlib.sha256)
    return mac.hexdigest()


def query_profile(uid: str):
    """Query a profile by id using parameterized queries to prevent SQL injection.

    uid must be a numeric string (and therefore an integer id).
    """
    if not uid or not uid.isdigit():
        return []
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("SELECT id,name,balance FROM profiles WHERE id = ?", (uid,))
        data = c.fetchall()
        return data
    finally:
        conn.close()


def _is_allowed_notify_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in ("https",):
        return False
    host = parsed.hostname or ""
    # If an allow-list is configured, require matching host
    if ALLOWED_NOTIFY_DOMAINS:
        return any(host == d or host.endswith("." + d) for d in ALLOWED_NOTIFY_DOMAINS)
    # otherwise reject localhost/internal IPs
    if host in ("localhost", "127.0.0.1"):
        return False
    return True


def transfer_funds(payload: dict):
    target = payload.get("target")
    amount = payload.get("amount")
    logger.info("transfer request: target=%s amount=%s", target, amount)
    url = payload.get("notify_url")
    if not url or not _is_allowed_notify_url(url):
        raise ValueError("notify_url is invalid or not allowed")
    try:
        resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount}, timeout=5)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        logger.exception("failed to notify %s: %s", url, e)
        raise


def update_records(path: str):
    """Load a YAML config from the controlled CONFIG_DIR. Path traversal is rejected.

    We only allow base filenames (no path separators) to avoid directory traversal.
    """
    if not path or os.path.basename(path) != path:
        raise ValueError("invalid config filename")
    file_path = os.path.normpath(os.path.join(CONFIG_DIR, path))
    # Ensure the file lives inside CONFIG_DIR
    if not file_path.startswith(os.path.abspath(CONFIG_DIR)):
        raise ValueError("invalid config path")
    if not os.path.exists(file_path):
        raise FileNotFoundError("config file not found")
    with open(file_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name: str):
    """Safely archive the database to a zip inside EXPORT_DIR.

    Reject names that include path separators or suspicious characters.
    """
    if not name or os.path.basename(name) != name:
        raise ValueError("invalid export name")
    # sanitized name for zip
    zip_path = os.path.join(EXPORT_DIR, f"{name}.zip")
    # Create zip with the DB_FILE inside; do not expose arbitrary shell execution
    try:
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(DB_FILE, arcname=os.path.basename(DB_FILE))
        return zip_path
    except Exception:
        logger.exception("failed to create export for %s", name)
        raise


def require_admin(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if not ADMIN_API_KEY or key != ADMIN_API_KEY:
            abort(401)
        return func(*args, **kwargs)
    wrapper.__name__ = getattr(func, "__name__", "wrapper")
    return wrapper


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json or {}
    try:
        token = auth_user(info)
    except Exception as e:
        logger.exception("auth error: %s", e)
        abort(400)
    return jsonify({"token": token})


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    return jsonify(query_profile(uid))


@app.route("/transfer", methods=["POST"])
@require_admin
def api_transfer():
    p = request.json or {}
    try:
        result = transfer_funds(p)
    except Exception as e:
        logger.exception("transfer failed: %s", e)
        abort(400, str(e))
    return jsonify({"result": result})


@app.route("/config", methods=["POST"])
@require_admin
def api_config():
    path = (request.json or {}).get("file")
    try:
        cfg = update_records(path)
    except Exception as e:
        logger.exception("config update failed: %s", e)
        abort(400, str(e))
    return jsonify(cfg)


@app.route("/export")
@require_admin
def api_export():
    name = request.args.get("name")
    try:
        zip_path = export_data(name)
    except Exception as e:
        logger.exception("export failed: %s", e)
        abort(400, str(e))
    return jsonify({"ok": 1, "file": zip_path})


if __name__ == "__main__":
    # Debug must be intentionally enabled - default is disabled for safety
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", debug=debug)
