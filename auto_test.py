import os
import platform
import subprocess
import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "test_run.log"


def detect_environment():
    system = platform.system().lower()
    in_docker = False
    try:
        if Path("/.dockerenv").exists():
            in_docker = True
        else:
            cgroup = Path("/proc/1/cgroup")
            if cgroup.exists() and "docker" in cgroup.read_text():
                in_docker = True
    except Exception:
        pass
    return system, in_docker


def run_tests_for_module(module_name: str):
    system, _ = detect_environment()
    env = os.environ.copy()
    env["MODULE_UNDER_TEST"] = module_name

    if system == "windows":
        cmd = ["cmd", "/c", "run_test.bat", module_name]
    else:
        cmd = ["bash", "run_test.sh", module_name]

    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout, proc.stderr


def log_run(module_name: str, returncode: int, stdout: str, stderr: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status = "TEST PASSED" if returncode == 0 else "TEST FAILED"

    lines = [
        f"===== {timestamp} module={module_name} =====",
        stdout.strip(),
        stderr.strip(),
        status,
        "",
    ]
    with LOG_FILE.open("a", encoding="utf-8") as f:
        for line in lines:
            if line:
                f.write(line + "\n")

    # Also print to console
    print("\n".join([l for l in lines if l]))


if __name__ == "__main__":
    modules = ["input_backup", "input"]
    results = {}
    for module in modules:
        rc, out, err = run_tests_for_module(module)
        results[module] = rc
        log_run(module, rc, out or "", err or "")

    # Exit non-zero only if the hardened module fails
    import sys
    sys.exit(results.get("input", 0))
