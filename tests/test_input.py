import os
import importlib
import sqlite3
from pathlib import Path
import pytest

MODULE_UNDER_TEST = os.environ.get("MODULE_UNDER_TEST", "input")
mod = importlib.import_module(MODULE_UNDER_TEST)


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE profiles (id INTEGER PRIMARY KEY, name TEXT, balance REAL)")
    cur.execute("INSERT INTO profiles (id, name, balance) VALUES (1, 'Alice', 100.0)")
    cur.execute("INSERT INTO profiles (id, name, balance) VALUES (2, 'Bob', 50.0)")
    conn.commit()
    conn.close()

    monkeypatch.setattr(mod, "DB_FILE", Path(db_path))
    return db_path


def test_auth_user_uses_strong_hash():
    token = mod.auth_user({"username": "alice"})
    assert isinstance(token, str)
    assert len(token) == 64  # SHA-256 hex digest length


@pytest.mark.parametrize("uid", ["1 OR 1=1", "abc", None])
def test_query_profile_blocks_injection(uid, temp_db):
    with pytest.raises(ValueError):
        mod.query_profile(uid)


def test_query_profile_returns_expected_row(temp_db):
    rows = mod.query_profile(1)
    assert rows == [(1, "Alice", 100.0)]


def test_transfer_rejects_insecure_url():
    payload = {"target": "acct", "amount": 10, "notify_url": "http://example.com"}
    with pytest.raises(ValueError):
        mod.transfer_funds(payload)


class DummyResponse:
    def __init__(self):
        self.status_code = 200
        self._json = {"ok": True}
        self.headers = {"content-type": "application/json"}

    def raise_for_status(self):
        return None

    def json(self):
        return self._json

    @property
    def text(self):
        return "ok"


def test_transfer_calls_requests_with_valid_url(monkeypatch):
    called = {}

    def fake_post(url, json=None, timeout=None, allow_redirects=None):  # noqa: A002 shadow builtins
        called.update({"url": url, "json": json, "timeout": timeout, "allow_redirects": allow_redirects})
        return DummyResponse()

    monkeypatch.setattr(mod, "requests", type("R", (), {"post": staticmethod(fake_post)}))

    payload = {"target": "acct", "amount": 10, "notify_url": "https://example.com"}
    result = mod.transfer_funds(payload)
    assert result == {"ok": True}
    assert called["url"] == "https://example.com"
    assert called["json"]["amount"] == 10


def test_update_records_allows_only_safe_config(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    cfg_file = cfg_dir / "settings.yaml"
    cfg_file.write_text("a: 1\n")

    monkeypatch.setattr(mod, "SAFE_CONFIG_DIR", cfg_dir)

    cfg = mod.update_records(cfg_file.name)
    assert cfg == {"a": 1}

    with pytest.raises(ValueError):
        mod.update_records("../inputs.py")


def test_export_data_sanitizes_name(tmp_path, monkeypatch):
    db_path = tmp_path / "db.sqlite"
    db_path.write_text("dummy")
    monkeypatch.setattr(mod, "DB_FILE", db_path)

    archive = mod.export_data("backup")
    assert Path(archive).is_file()

    with pytest.raises(ValueError):
        mod.export_data("bad;rm -rf")
