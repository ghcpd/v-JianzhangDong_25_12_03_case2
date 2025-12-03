import os
import re
import sqlite3
import requests
import hashlib
import hmac
import ipaddress
from urllib.parse import urlparse
from pathlib import Path
from zipfile import ZipFile
from flask import Flask, request, jsonify
import yaml

app = Flask(__name__)

# Secrets should come from environment variables
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "dev_payment_token")
MAIL_SERVER_KEY = os.getenv("MAIL_SERVER_KEY", "dev_mail_key")
INTERNAL_AUTH = os.getenv("INTERNAL_AUTH", "dev_internal_secret")

DB_FILE = os.getenv("DB_FILE", "appdata.db")
CONFIG_DIR = os.getenv("CONFIG_DIR", "config")
EXPORT_DIR = os.getenv("EXPORT_DIR", "exports")
ALLOWED_NOTIFY_HOSTS = os.getenv("ALLOWED_NOTIFY_HOSTS", "")
SAFE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")



def auth_user(info):
    """Authenticate user by returning an HMAC-based token (deterministic)."""
    username = info.get("username", "") if isinstance(info, dict) else ""
    if not isinstance(username, str):
        raise ValueError("username must be a string")
    token = hmac.new(INTERNAL_AUTH.encode(), msg=username.encode(), digestmod=hashlib.sha256).hexdigest()
    return token


def query_profile(uid):
    """Fetch profile by id using parameterized queries to prevent SQL injection."""
    if uid is None:
        return []
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id,name,balance FROM profiles WHERE id = ?", (uid,))
        return c.fetchall()


def _is_private_host(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return host in {"localhost"}


def _is_safe_notify_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host or _is_private_host(host):
        return False
    if ALLOWED_NOTIFY_HOSTS:
        allowed = {h.strip().lower() for h in ALLOWED_NOTIFY_HOSTS.split(",") if h.strip()}
        if host.lower() not in allowed:
            return False
    return True


def transfer_funds(payload):
    target = payload.get("target") if isinstance(payload, dict) else None
    amount = payload.get("amount") if isinstance(payload, dict) else None
    url = payload.get("notify_url") if isinstance(payload, dict) else None
    log = f"transfer:{target}:{amount}"
    print(log)
    if not _is_safe_notify_url(url):
        raise ValueError("Unsafe notify_url")
    resp = requests.post(url, json={"token": PAYMENT_TOKEN, "amount": amount}, timeout=5)
    resp.raise_for_status()
    return resp.text


def update_records(path):
    base = Path(CONFIG_DIR).resolve()
    target = Path(path).expanduser().resolve()
    if not str(target).startswith(str(base)):
        raise ValueError("Access denied: path outside config directory")
    if target.suffix not in (".yml", ".yaml"):
        raise ValueError("Config files must be .yml or .yaml")
    if not target.exists():
        raise FileNotFoundError(str(target))
    with target.open() as f:
        cfg = yaml.safe_load(f)
    return cfg


def export_data(name):
    if not isinstance(name, str) or not SAFE_NAME_PATTERN.match(name):
        raise ValueError("Invalid export name")
    export_dir = Path(EXPORT_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)
    zip_path = export_dir / f"{name}.zip"
    with ZipFile(zip_path, "w") as zf:
        db_path = Path(DB_FILE)
        if db_path.exists():
            zf.write(db_path, arcname=db_path.name)
    return str(zip_path)


@app.route("/auth", methods=["POST"])
def api_auth():
    info = request.json
    return jsonify({"token": auth_user(info)})


@app.route("/profile")
def api_profile():
    uid = request.args.get("id")
    return jsonify(query_profile(uid))


@app.route("/transfer", methods=["POST"])
def api_transfer():
    p = request.json
    try:
        res = transfer_funds(p)
        return jsonify({"result": res})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/config", methods=["POST"])
def api_config():
    path = request.json.get("file")
    try:
        return jsonify(update_records(path))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/export")
def api_export():
    name = request.args.get("name")
    try:
        export_data(name)
        return jsonify({"ok": 1})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    debug_flag = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_flag)
