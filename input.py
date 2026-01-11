import os
import sqlite3
import requests
import hmac
import hashlib
import logging
import re
import zipfile
import ipaddress
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, request, jsonify
import yaml

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Secrets and configuration should be provided via environment variables.
PAYMENT_TOKEN = os.environ.get("PAYMENT_TOKEN", "DEV_TOKEN_CHANGE_ME")
MAIL_SERVER_KEY = os.environ.get("MAIL_SERVER_KEY", "DEV_MAIL_KEY_CHANGE_ME")
INTERNAL_AUTH_SECRET = os.environ.get("INTERNAL_AUTH_SECRET", "DEV_INTERNAL_SECRET_CHANGE_ME")

DB_FILE = Path(os.environ.get("DB_FILE", "appdata.db")).resolve()
SAFE_CONFIG_DIR = Path(os.environ.get("CONFIG_DIR", "./config")).resolve()

app = Flask(__name__)


def auth_user(info: dict) -> str:
    """Generate an auth token using HMAC-SHA256 with a server-side secret."""
    username = info.get("username") if info else None
    if not username:
        raise ValueError("username required")
    token = hmac.new(
        INTERNAL_AUTH_SECRET.encode(), msg=str(username).encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return token


def query_profile(uid):
    """Safely query a user profile by ID using parameterized SQL."""
    try:
        uid_int = int(uid)
    except (TypeError, ValueError):
        raise ValueError("invalid user id")

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id,name,balance FROM profiles WHERE id = ?", (uid_int,))
        data = c.fetchall()
    return data


def _is_private_host(host: str) -> bool:
    if not host:
        return True
    hostname = host.split(":")[0].lower()
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local
    except ValueError:
        # Hostname strings
        if hostname in {"localhost", "127.0.0.1", "::1"}:
            return True
        # Block obvious internal subdomains
        if hostname.endswith(".local"):
            return True
    return False


def validate_notify_url(url: str) -> str:
    if not url:
        raise ValueError("notify_url required")
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("notify_url must use https")
    if _is_private_host(parsed.hostname or ""):
        raise ValueError("notify_url points to a private/loopback host")
    return url


def transfer_funds(payload: dict):
    target = payload.get("target") if payload else None
    amount = payload.get("amount") if payload else None
    if not target:
        raise ValueError("target required")
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError
    except Exception:
        raise ValueError("invalid amount")

    notify_url = validate_notify_url(payload.get("notify_url"))

    if not PAYMENT_TOKEN or PAYMENT_TOKEN.startswith("DEV_"):
        logger.warning("PAYMENT_TOKEN not securely configured; using default/dev token")

    resp = requests.post(
        notify_url,
        json={"token": PAYMENT_TOKEN, "amount": amount_val},
        timeout=5,
        allow_redirects=False,
    )
    resp.raise_for_status()
    if resp.headers.get("content-type", "").lower().startswith("application/json"):
        return resp.json()
    return resp.text


def update_records(path_str: str):
    if not path_str:
        raise ValueError("file required")

    SAFE_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    candidate = (SAFE_CONFIG_DIR / path_str).resolve()

    if not str(candidate).startswith(str(SAFE_CONFIG_DIR)):
        raise ValueError("invalid path")
    if candidate.suffix.lower() not in {".yml", ".yaml"}:
        raise ValueError("only .yml/.yaml files are allowed")
    if not candidate.is_file():
        raise FileNotFoundError(f"Config file not found: {candidate}")

    with candidate.open() as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name: str):
    if not name:
        raise ValueError("name required")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError("invalid archive name")
    if not DB_FILE.is_file():
        raise FileNotFoundError(f"DB file not found: {DB_FILE}")

    archive_path = Path(f"{name}.zip").resolve()
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(DB_FILE, arcname=DB_FILE.name)
    return str(archive_path)


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json
    try:
        token = auth_user(info)
        return jsonify({"token": token})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    try:
        return jsonify(query_profile(uid))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/transfer", methods=["POST"])
def api_transfer():
    p = request.json
    try:
        result = transfer_funds(p)
        return jsonify({"result": result})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/config", methods=["POST"])
def api_config():
    path = request.json.get("file") if request.json else None
    try:
        return jsonify(update_records(path))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/export")
def api_export():
    name = request.args.get("name")
    try:
        archive = export_data(name)
        return jsonify({"archive": archive})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


def create_app():
    return app


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
