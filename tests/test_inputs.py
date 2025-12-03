import os
import sqlite3
import importlib
import tempfile
import pytest


MODULE_NAME = os.getenv("TEST_TARGET", "inputs").strip()


def load_module(name):
    if name in globals():
        return globals()[name]
    mod = importlib.import_module(name)
    importlib.reload(mod)
    globals()[name] = mod
    return mod


def make_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS profiles (id TEXT PRIMARY KEY, name TEXT, balance REAL)")
    c.execute("INSERT OR REPLACE INTO profiles (id,name,balance) VALUES ('1','Alice',100)")
    c.execute("INSERT OR REPLACE INTO profiles (id,name,balance) VALUES ('2','Bob',50)")
    conn.commit()
    conn.close()


def test_sql_injection_behavior(tmp_path):
    mod = load_module(MODULE_NAME)
    dbfile = str(tmp_path / "test.db")
    make_db(dbfile)
    # point the module at our test DB
    setattr(mod, "DB_FILE", dbfile)

    # injection string that would return all rows if SQL is not parameterized
    inj = "1' OR '1'='1"
    result = mod.query_profile(inj)
    # Secure behavior: parameterized queries must prevent SQL injection
    assert result == [], "SQL injection should be prevented by parameterized queries"

    # valid id should work in both
    r1 = mod.query_profile("1")
    assert len(r1) == 1


def test_update_records_path_restriction(tmp_path):
    mod = load_module(MODULE_NAME)

    # create a configs dir and a safe file
    configs = tmp_path / "configs"
    configs.mkdir()
    safe_file = configs / "safe.yaml"
    safe_file.write_text("foo: bar")

    # put a secret file outside configs
    secret = tmp_path / "secret.yaml"
    secret.write_text("super: secret")

    # For the secure module, set CONFIG_DIR to our configs directory
    setattr(mod, "CONFIG_DIR", str(configs))

    # Secure behavior: only allow basenames in CONFIG_DIR
    res = mod.update_records("safe.yaml")
    assert isinstance(res, dict)
    assert res.get("foo") == "bar"
    # traversal should be rejected
    with pytest.raises(Exception):
        mod.update_records("../secret.yaml")


def test_export_behavior(tmp_path):
    mod = load_module(MODULE_NAME)

    dbfile = str(tmp_path / "test2.db")
    make_db(dbfile)
    setattr(mod, "DB_FILE", dbfile)

    name = "safe_export"
    # Secure behavior: should create a zip and return a path
    zpath = mod.export_data(name)
    assert isinstance(zpath, str)
    assert os.path.exists(zpath)


def test_transfer_url_validation():
    mod = load_module(MODULE_NAME)
    payload = {"target": "x", "amount": 10, "notify_url": "ftp://example.com"}
    # Secure behavior: reject non-https URLs / not-allowed host
    with pytest.raises(ValueError):
        mod.transfer_funds(payload)
