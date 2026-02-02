import os
import subprocess
import platform
from datetime import datetime

FILES = ['inputs_backup.py', 'inputs.py']
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'test_run.log')


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def now():
    return datetime.utcnow().isoformat() + 'Z'


def run_script_for_file(file):
    system = platform.system()
    if os.path.exists('/.dockerenv') or os.environ.get('IN_DOCKER') == '1':
        system = 'Docker'

    if system == 'Windows':
        cmd = ['cmd.exe', '/c', 'run_test.bat', file]
    else:
        cmd = ['bash', 'run_test.sh', file]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.returncode, proc.stdout


def main():
    ensure_log_dir()
    all_ok = True
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        for file in FILES:
            ts = now()
            f.write(f"[{ts}] START TEST {file}\n")
            ret, out = run_script_for_file(file)
            f.write(out)
            status = 'TEST PASSED' if ret == 0 else 'TEST FAILED'
            f.write(f"[{now()}] {file} {status} (exit {ret})\n\n")
            if ret != 0:
                all_ok = False

    final_status = 'TEST PASSED' if all_ok else 'TEST FAILED'
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{now()}] FINAL STATUS: {final_status}\n")

    print(final_status)
    return 0 if all_ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
