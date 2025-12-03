# Security Audit & Hardening

## Overview
- `inputs.py`: Hardened application with mitigations (SQLi, SSRF, command injection, path traversal, secret management).
- `input_backup.py`: Original vulnerable file (for comparison/testing).
- `tests_runner.py`: Python test harness to validate security behaviors.
- `run_test.sh` / `run_test.bat`: Platform-specific wrappers to run `tests_runner.py`.
- `auto_test.py`: Detects OS/Docker, runs appropriate test script for both `input_backup.py` and `inputs.py`, logs results.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Containerized environment.
- `setup.sh`: Convenience script to create virtualenv and install dependencies.
- `logs/test_run.log`: Test run log with timestamps and final status.
- `report.json`: Structured vulnerability report with fixes.

## Setup
### Prerequisites
- Python 3.9+
- `pip` available
- (Optional) Docker

### Virtualenv (Linux/macOS)
```bash
chmod +x setup.sh
./setup.sh
```

### Virtualenv (Windows PowerShell)
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### Docker
```bash
docker build -t secure-app .
docker run --rm -p 5000:5000 secure-app
```

## Running Tests
### Linux/macOS
```bash
chmod +x run_test.sh
./run_test.sh inputs.py       # secure version
./run_test.sh input_backup.py # vulnerable version
```

### Windows
```powershell
.\run_test.bat inputs.py
.\run_test.bat input_backup.py
```

## Automatic Testing & Logging
```bash
python auto_test.py
```
- Detects OS/Docker and runs the appropriate test script for both files.
- Writes logs to `logs/test_run.log` with timestamps and per-file status.
- Final line in log: `TEST PASSED` or `TEST FAILED`.

## Interpreting Logs
- Each test run logs `stdout` and `stderr` for the module under test.
- `Status for <module>: PASS/FAIL (exit=<code>)`
- Final line indicates overall result across modules.

## Environment Variables
- `PAYMENT_TOKEN`, `MAIL_SERVER_KEY`, `INTERNAL_AUTH`: secrets for `inputs.py` (fallback dev defaults).
- `DB_FILE`, `CONFIG_DIR`, `EXPORT_DIR`, `ALLOWED_NOTIFY_HOSTS`: override defaults for storage and network allowlisting.
- `FLASK_DEBUG`: set to `1` to enable debug (default: disabled).
