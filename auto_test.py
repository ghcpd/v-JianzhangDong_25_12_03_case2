import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "test_run.log"

MODULES = ["input_backup.py", "inputs.py"]


def detect_env():
    if os.name == "nt":
        return "windows"
    if Path("/.dockerenv").exists() or os.getenv("DOCKER"):
        return "docker"
    return "linux"


def run_script(script: str, module: str):
    if script.endswith(".sh"):
        cmd = ["bash", script, module]
    else:
        cmd = [script, module]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def log(msg: str):
    ts = datetime.now(timezone.utc).isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def main():
    env = detect_env()
    script = "run_test.bat" if env == "windows" else "run_test.sh"
    overall_pass = True
    for module in MODULES:
        ts = datetime.now(timezone.utc).isoformat()
        log(f"Starting tests for {module} using {script}")
        rc, out, err = run_script(script, module)
        if out:
            log(f"stdout for {module}:\n{out}")
        if err:
            log(f"stderr for {module}:\n{err}")
        expected_fail = module == "input_backup.py"
        status = "PASS" if rc == 0 else "FAIL"
        if expected_fail and rc != 0:
            status = "EXPECTED_FAIL"
        log(f"Status for {module}: {status} (exit={rc})")
        if not expected_fail and rc != 0:
            overall_pass = False
    final_status = "TEST PASSED" if overall_pass else "TEST FAILED"
    log(final_status)
    print(final_status)
    raise SystemExit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
