#!/usr/bin/env bash
set -e
PYTHON=${PYTHON:-python3}
if [ $# -lt 1 ]; then
  echo "Usage: run_test.sh <file>"
  exit 2
fi
FILE=$1
$PYTHON test_inputs.py "$FILE"
