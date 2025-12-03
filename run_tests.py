#!/usr/bin/env python3
import os
import subprocess
import datetime
from pathlib import Path

ROOT = Path(__file__).parent
LOG = ROOT / "logs" / "test_run.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

TARGETS = ["input_backup", "inputs_backup", "inputs"]


def ts():
    return datetime.datetime.utcnow().isoformat() + "Z"


def run_target(target):
    env = os.environ.copy()
    env["TEST_TARGET"] = target
    cmd = [os.environ.get("PYTHON", "python"), "-m", "pytest", "-q", "tests/test_inputs.py"]
    start = ts()
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True) as p:
        out, _ = p.communicate()
        rc = p.returncode
    return start, rc, out


def main():
    overall_ok = True
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"=== RUN_TESTS START {ts()} ===\n")
        for target in TARGETS:
            fh.write(f"===== TEST START: {target} at {ts()} =====\n")
            fh.flush()
            start, rc, out = run_target(target)
            fh.write(out)
            if rc == 0:
                fh.write(f"[{ts()}] {target} TEST PASSED\n\n")
            else:
                fh.write(f"[{ts()}] {target} TEST FAILED (exit={rc})\n\n")
                overall_ok = False
        final = "TEST PASSED" if overall_ok else "TEST FAILED"
        fh.write(final + "\n")
        fh.write(f"=== RUN_TESTS END {ts()} ===\n\n")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
