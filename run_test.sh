#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/logs"
SUMMARY_LOG="$ROOT/logs/test_run.log"
: > "$SUMMARY_LOG"

PYTHON_CMD=python
if [ -x ".venv/bin/python" ]; then
  PYTHON_CMD=.venv/bin/python
fi

# delegate to run_tests.py (portable runner)
"$PYTHON_CMD" run_tests.py
exit $?
