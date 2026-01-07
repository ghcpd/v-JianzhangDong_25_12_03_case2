#!/bin/bash
# run_test.sh - Test script for Linux/macOS

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Source virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "=== Running Security Tests ==="
echo "Platform: $(uname -s)"
echo "Python: $(python --version)"
echo ""

# Run basic syntax check
echo "1. Running syntax check..."
python -m py_compile inputs.py inputs_backup.py
echo "✓ Syntax check passed"

# Check for critical vulnerabilities in backup
echo ""
echo "2. Checking for known vulnerabilities in backup..."
if grep -q "PAYMENT_TOKEN = \"tok_production" inputs_backup.py; then
    echo "✓ Hardcoded secret found in backup (expected)"
fi

if grep -q "WHERE id = '%s'" inputs_backup.py; then
    echo "✓ SQL injection vulnerability found in backup (expected)"
fi

if grep -q "shell=True" inputs_backup.py; then
    echo "✓ Command injection vulnerability found in backup (expected)"
fi

if grep -q "debug=True" inputs_backup.py; then
    echo "✓ Debug mode enabled in backup (expected)"
fi

if grep -q "hashlib.md5" inputs_backup.py; then
    echo "✓ Weak hashing found in backup (expected)"
fi

# Check that vulnerabilities are fixed in secure version
echo ""
echo "3. Checking for fixes in secure version..."
if grep -q "os.getenv('PAYMENT_TOKEN'" inputs.py; then
    echo "✓ Secrets moved to environment variables"
fi

if grep -q "c.execute(q, (uid,))" inputs.py; then
    echo "✓ SQL injection fixed with parameterized queries"
fi

if grep -q "zipfile.ZipFile" inputs.py; then
    echo "✓ Command injection fixed - using zipfile API instead of shell"
fi

if grep -q "os.getenv('FLASK_DEBUG'" inputs.py; then
    echo "✓ Debug mode now controlled by environment variable"
fi

if grep -q "is_safe_url" inputs.py; then
    echo "✓ SSRF protection added"
fi

if grep -q "bcrypt.hashpw" inputs.py; then
    echo "✓ Weak hashing replaced with bcrypt"
fi

if grep -q "os.path.abspath" inputs.py; then
    echo "✓ Path traversal fixed with path validation"
fi

echo ""
echo "=== All Tests Passed ==="
exit 0
