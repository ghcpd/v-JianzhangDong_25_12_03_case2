# inputs.py security hardening and tests ✅

Overview
- This repository contains an audited and hardened `inputs.py` (original saved as `inputs_backup.py`) plus automated tests and environment scripts to validate fixes.

Key files
- `inputs.py` — Secured implementation (secrets read from environment, SQL parameterization, SSRF checks, no shell=True).
- `inputs_backup.py` — Original, vulnerable file (backup).
- `test_inputs.py` — Static scanner script that checks for insecure patterns in a file.
- `run_test.sh` / `run_test.bat` — Platform-specific wrappers to run `test_inputs.py`.
- `auto_test.py` — Cross-platform runner that detects environment and executes the appropriate test script for `inputs_backup.py` and `inputs.py`, logging results in `logs/test_run.log`.
- `report.json` — Structured vulnerability report with fixes.
- `requirements.txt` — Python dependencies.
- `Dockerfile` / `setup.sh` — Environment replication scripts.

Setup (Linux/macOS)
1. Create a Python virtualenv and install dependencies:
   - `bash setup.sh`

2. Set required environment variables (example):
   - `export PAYMENT_TOKEN=your_token`
   - `export INTERNAL_AUTH=your_secret`
   - `export ADMIN_API_KEY=admin_key`
   - optionally `export CONFIG_DIR=./config` and `export ALLOWED_NOTIFY_HOSTS=example.com`

Running tests
- Linux/macOS: `bash run_test.sh inputs.py` (or `inputs_backup.py`).
- Windows: `run_test.bat inputs.py`.
- Automatic: `python auto_test.py` — runs both `inputs_backup.py` and `inputs.py` tests and writes `logs/test_run.log` with timestamps and final statuses.

Docker
- Build: `docker build -t inputs-test .`
- Run: `docker run --rm inputs-test` (this will execute `auto_test.py` in container)

Interpreting logs
- Check `logs/test_run.log` for timestamped outputs of each test and a final summary line: `TEST PASSED` or `TEST FAILED`.

Notes
- Ensure secrets are set as environment variables in deployment.
- The test scanner is heuristic-based and intended to catch the most common insecure patterns present in the original file.
