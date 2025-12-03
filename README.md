# Security audit and test harness for inputs.py

This repository contains a security audit and fixes for `inputs.py` (backup saved to `inputs_backup.py`), plus tests and scripts to verify the vulnerability fixes.

Files generated in this change:

- `inputs_backup.py` — original file (backup of the vulnerable implementation)
- `inputs.py` — secured / upgraded implementation
- `tests/test_inputs.py` — pytest tests that compare the backup and fixed modules
- `run_test.sh` — POSIX shell script to run tests for both modules and log results
- `run_test.bat` — Windows batch script to run tests for both modules and log results
- `auto_test.py` — auto-run script that selects the correct test script for the platform and appends results to `logs/test_run.log`
- `report.json` — structured audit report describing vulnerabilities and fixes
- `requirements.txt` — dependencies for running tests
- `Dockerfile` — container image to run tests
- `setup.sh` — create virtualenv and install dependencies
- `logs/` — directory where test logs will be collected

Quick setup (Linux/macOS):

1. Create a virtual environment and install dependencies:

```bash
./setup.sh
```

2. Run tests directly (POSIX):

```bash
./run_test.sh
```

Windows (PowerShell/CMD):

```powershell
.\run_test.bat
```

Automatic runner:

```bash
python auto_test.py
```

Logs: check `logs/test_run.log` for a timestamped record of the runs. The log includes per-module outputs and final lines like `TEST PASSED` or `TEST FAILED`.

Notes:
- Secrets are expected to be provided via environment variables for `inputs.py` (PAYMENT_TOKEN, MAIL_SERVER_KEY, INTERNAL_AUTH_KEY, ADMIN_API_KEY).
- Tests are driven by the `TEST_TARGET` environment variable: `inputs_backup` or `inputs` (default value in `run_test.sh` chooses both).
