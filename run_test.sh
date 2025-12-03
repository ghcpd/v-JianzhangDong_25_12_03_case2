#!/usr/bin/env bash
set -euo pipefail
MODULE=${1:-${MODULE_UNDER_TEST:-input}}
export MODULE_UNDER_TEST="$MODULE"
python -m pytest -q
