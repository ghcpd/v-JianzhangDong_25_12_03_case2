import argparse
import importlib.util
import os
import sqlite3
import sys
import tempfile
import types
from pathlib import Path


def import_module_from_path(path: str, module_name: str = None) -> types.ModuleType:
    module_name = module_name or Path(path).stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    loader.exec_module(module)  # type: ignore
    return module


def setup_db(db_path: Path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS profiles (id TEXT PRIMARY KEY, name TEXT, balance REAL)")
    c.execute("DELETE FROM profiles")
    c.executemany(
        "INSERT INTO profiles (id, name, balance) VALUES (?, ?, ?)",
        [("1", "Alice", 100.0), ("2", "Bob", 50.0)],
    )
    conn.commit()
    conn.close()


def test_sql_injection(module) -> bool:
    # Expect: secure module returns 0 or 1 row for literal injection string
    r1 = module.query_profile("1")
    r2 = module.query_profile("1' OR '1'='1")
    return len(r1) == 1 and len(r2) <= 1


def test_command_injection(module, tmpdir: Path) -> bool:
    os.chdir(tmpdir)
    inj_file = tmpdir / "injection.txt"
    if os.name == "nt":
        name = "test_export & echo vulnerable > injection.txt & rem"
    else:
        name = "test_export; echo vulnerable > injection.txt; #"
    try:
        module.export_data(name)
    except Exception:
        pass
    return not inj_file.exists()


def test_path_traversal(module, tmpdir: Path) -> bool:
    config_dir = tmpdir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    allowed = config_dir / "conf.yaml"
    allowed.write_text("ok: true")
    outside = tmpdir / "secret.yaml"
    outside.write_text("secret: true")
    try:
        module.update_records(str(allowed))
        ok_allowed = True
    except Exception:
        ok_allowed = False
    try:
        module.update_records(str(outside))
        outside_allowed = True
    except Exception:
        outside_allowed = False
    return ok_allowed and not outside_allowed


def test_ssrf(module) -> bool:
    class DummyResp:
        def __init__(self):
            self.text = "ok"

        def raise_for_status(self):
            return None

    captured = []

    def fake_post(url, json=None, timeout=None):
        captured.append(url)
        return DummyResp()

    orig_post = module.requests.post
    module.requests.post = fake_post

    payload = {"target": "T", "amount": 10, "notify_url": "http://169.254.169.254/latest"}
    try:
        module.transfer_funds(payload)
        vulnerable = True  # should have rejected
    except Exception:
        vulnerable = False
    finally:
        module.requests.post = orig_post
    return not vulnerable


def run_tests(module_path: str) -> bool:
    module_name = Path(module_path).stem
    # Set environment for module import
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        tmpdir = Path(td)
        os.environ["DB_FILE"] = str(tmpdir / "appdata.db")
        os.environ["CONFIG_DIR"] = str(tmpdir / "config")
        os.environ["EXPORT_DIR"] = str(tmpdir / "exports")
        os.environ["ALLOWED_NOTIFY_HOSTS"] = "example.com"
        # Import module
        module = import_module_from_path(module_path, module_name)
        # set up DB
        setup_db(Path(module.DB_FILE))
        # Run tests
        results = {}
        results["sql_injection"] = test_sql_injection(module)
        results["command_injection"] = test_command_injection(module, tmpdir)
        results["path_traversal"] = test_path_traversal(module, tmpdir)
        results["ssrf"] = test_ssrf(module)
        all_pass = all(results.values())
        print(f"Test results for {module_name}:")
        for k, v in results.items():
            print(f"  {k}: {'PASS' if v else 'FAIL'}")
        print(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")
        return all_pass


def main():
    parser = argparse.ArgumentParser(description="Run security tests on module")
    parser.add_argument("--module", default="inputs.py", help="Path to module file")
    args = parser.parse_args()
    success = run_tests(args.module)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
