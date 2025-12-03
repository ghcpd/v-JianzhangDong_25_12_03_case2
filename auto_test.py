#!/usr/bin/env python3
import os
import platform
import subprocess
import datetime
from pathlib import Path

LOG_FILE = Path("logs") / "test_run.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _timestamp():
    return datetime.datetime.utcnow().isoformat() + "Z"


def run_script(cmd, env=None):
    # run command and return (exitcode, combined_output)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    out, _ = proc.communicate()
    return proc.returncode, out.decode(errors="replace")


def main():
    system = platform.system()
    if system == "Windows":
        script = "run_test.bat"
    else:
        script = "./run_test.sh"

    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(f"=== AUTO TEST RUN START: {_timestamp()} ===\n")
        fh.flush()
        code, out = run_script(script)
        fh.write(out)
        fh.write("\n")
        status_line = "TEST PASSED" if code == 0 else "TEST FAILED"
        fh.write(f"{_timestamp()} {script} exit={code} {status_line}\n")
        fh.write("=== AUTO TEST RUN END ===\n\n")

    print(f"Wrote logs to {LOG_FILE}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
