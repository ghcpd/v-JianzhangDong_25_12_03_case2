#!/usr/bin/env bash
set -euo pipefail
MODULE=${1:-inputs.py}
python tests_runner.py --module "$MODULE"
