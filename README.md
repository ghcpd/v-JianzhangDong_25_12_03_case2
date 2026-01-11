# Security Audit & Hardening for `input.py`

## Overview
- `inputs.py` — Original provided source (unchanged).
- `input_backup.py` — Backup of the original insecure code.
- `input.py` — Hardened, secure implementation.
- `report.json` — Structured vulnerability report with line numbers, severities, and fixes.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — Containerized environment for running the app/tests.
- `setup.sh` — Linux/macOS setup (venv + deps).
- `run_test.sh` / `run_test.bat` — Test runners for Linux/macOS and Windows.
- `auto_test.py` — Runs tests for both `input_backup.py` and `input.py`, logs results to `logs/test_run.log`.
- `tests/` — Pytest suite verifying applied security fixes.

## Setup
### Linux/macOS
```bash
chmod +x setup.sh run_test.sh
./setup.sh
```

### Windows (PowerShell)
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Running Tests
### Linux/macOS
```bash
./run_test.sh            # defaults to MODULE_UNDER_TEST=input
./run_test.sh input_backup
```

### Windows
```bat
run_test.bat             # defaults to MODULE_UNDER_TEST=input
run_test.bat input_backup
```

## Automatic Test Runner
```bash
python auto_test.py
```
- Detects OS/Docker and invokes the appropriate test script.
- Runs tests sequentially for `input_backup` then `input`.
- Logs outputs and statuses to `logs/test_run.log`.

## Logs
- Log file: `logs/test_run.log`
- Each block includes a UTC timestamp, module name, captured output, and a final status line:
  - `TEST PASSED` or `TEST FAILED`

## Docker
```bash
docker build -t secure-input .
docker run --rm -p 5000:5000 secure-input
```

## Notes
- Configure secrets via environment variables: `PAYMENT_TOKEN`, `MAIL_SERVER_KEY`, `INTERNAL_AUTH_SECRET`, `DB_FILE`, `CONFIG_DIR`.
- Default dev placeholders are provided; **do not** use them in production.
