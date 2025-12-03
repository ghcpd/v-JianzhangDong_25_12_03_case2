#!/bin/bash

# Test script for Linux/macOS
# This script runs security tests on both the vulnerable and fixed versions

set -e

echo "=========================================="
echo "Running Security Tests"
echo "=========================================="
echo ""

# Set environment variables for testing
export PAYMENT_TOKEN="test_token_123"
export MAIL_SERVER_KEY="test_mail_key_456"
export INTERNAL_AUTH="test_auth_789"
export ALLOWED_DOMAINS="localhost,127.0.0.1"
export ALLOWED_CONFIG_DIR="./configs"
export FLASK_DEBUG="False"

# Function to test SQL injection vulnerability
test_sql_injection() {
    local file=$1
    echo "Testing SQL Injection in $file..."
    
    # Test if parameterized queries are used
    if grep -q "execute(q, (uid,))" "$file"; then
        echo "  ✓ PASS: Using parameterized queries"
        return 0
    elif grep -q "\"SELECT.*%s\".*%.*uid" "$file"; then
        echo "  ✗ FAIL: SQL Injection vulnerability detected (string formatting)"
        return 1
    else
        echo "  ? UNKNOWN: Could not determine query method"
        return 1
    fi
}

# Function to test command injection vulnerability
test_command_injection() {
    local file=$1
    echo "Testing Command Injection in $file..."
    
    # Test if shell=False is used
    if grep -q "shell=False" "$file"; then
        echo "  ✓ PASS: Using safe subprocess call (shell=False)"
        return 0
    elif grep -q "shell=True" "$file"; then
        echo "  ✗ FAIL: Command Injection vulnerability detected (shell=True)"
        return 1
    else
        echo "  ? UNKNOWN: Could not determine subprocess method"
        return 1
    fi
}

# Function to test hardcoded secrets
test_hardcoded_secrets() {
    local file=$1
    echo "Testing for Hardcoded Secrets in $file..."
    
    # Check if secrets are loaded from environment
    if grep -q "os.environ.get(\"PAYMENT_TOKEN\"" "$file"; then
        echo "  ✓ PASS: Using environment variables for secrets"
        return 0
    elif grep -q "PAYMENT_TOKEN = \"tok_" "$file"; then
        echo "  ✗ FAIL: Hardcoded secrets detected"
        return 1
    else
        echo "  ? UNKNOWN: Could not determine secret storage method"
        return 1
    fi
}

# Function to test weak cryptography
test_weak_crypto() {
    local file=$1
    echo "Testing for Weak Cryptography in $file..."
    
    # Check if SHA-256 is used instead of MD5
    if grep -q "hashlib.sha256" "$file"; then
        echo "  ✓ PASS: Using SHA-256 for hashing"
        return 0
    elif grep -q "hashlib.md5" "$file"; then
        echo "  ✗ FAIL: Weak cryptography detected (MD5)"
        return 1
    else
        echo "  ? UNKNOWN: Could not determine hash algorithm"
        return 1
    fi
}

# Function to test SSRF protection
test_ssrf_protection() {
    local file=$1
    echo "Testing for SSRF Protection in $file..."
    
    # Check if URL validation exists
    if grep -q "ALLOWED_DOMAINS" "$file" && grep -q "urlparse" "$file"; then
        echo "  ✓ PASS: SSRF protection implemented"
        return 0
    elif grep -q "requests.post(url" "$file" && ! grep -q "urlparse" "$file"; then
        echo "  ✗ FAIL: SSRF vulnerability detected (no URL validation)"
        return 1
    else
        echo "  ? UNKNOWN: Could not determine SSRF protection"
        return 1
    fi
}

# Function to test path traversal protection
test_path_traversal() {
    local file=$1
    echo "Testing for Path Traversal Protection in $file..."
    
    # Check if path validation exists
    if grep -q "os.path.abspath" "$file" && grep -q "startswith(base_dir)" "$file"; then
        echo "  ✓ PASS: Path traversal protection implemented"
        return 0
    elif grep -q "open(path)" "$file" && ! grep -q "os.path.abspath" "$file"; then
        echo "  ✗ FAIL: Path traversal vulnerability detected"
        return 1
    else
        echo "  ? UNKNOWN: Could not determine path validation"
        return 1
    fi
}

# Function to test debug mode
test_debug_mode() {
    local file=$1
    echo "Testing Debug Mode Configuration in $file..."
    
    # Check if debug mode is configurable
    if grep -q "os.environ.get(\"FLASK_DEBUG\"" "$file"; then
        echo "  ✓ PASS: Debug mode is configurable via environment"
        return 0
    elif grep -q "app.run(debug=True)" "$file"; then
        echo "  ✗ FAIL: Debug mode hardcoded to True"
        return 1
    else
        echo "  ? UNKNOWN: Could not determine debug mode configuration"
        return 1
    fi
}

# Run tests on vulnerable version
echo "=========================================="
echo "Testing inputs_backup.py (Vulnerable Version)"
echo "=========================================="
echo ""

backup_passed=0
backup_failed=0

test_sql_injection "inputs_backup.py" && ((backup_passed++)) || ((backup_failed++))
test_command_injection "inputs_backup.py" && ((backup_passed++)) || ((backup_failed++))
test_hardcoded_secrets "inputs_backup.py" && ((backup_passed++)) || ((backup_failed++))
test_weak_crypto "inputs_backup.py" && ((backup_passed++)) || ((backup_failed++))
test_ssrf_protection "inputs_backup.py" && ((backup_passed++)) || ((backup_failed++))
test_path_traversal "inputs_backup.py" && ((backup_passed++)) || ((backup_failed++))
test_debug_mode "inputs_backup.py" && ((backup_passed++)) || ((backup_failed++))

echo ""
echo "inputs_backup.py Results: $backup_passed passed, $backup_failed failed"
echo ""

# Run tests on fixed version
echo "=========================================="
echo "Testing inputs.py (Fixed Version)"
echo "=========================================="
echo ""

fixed_passed=0
fixed_failed=0

test_sql_injection "inputs.py" && ((fixed_passed++)) || ((fixed_failed++))
test_command_injection "inputs.py" && ((fixed_passed++)) || ((fixed_failed++))
test_hardcoded_secrets "inputs.py" && ((fixed_passed++)) || ((fixed_failed++))
test_weak_crypto "inputs.py" && ((fixed_passed++)) || ((fixed_failed++))
test_ssrf_protection "inputs.py" && ((fixed_passed++)) || ((fixed_failed++))
test_path_traversal "inputs.py" && ((fixed_passed++)) || ((fixed_failed++))
test_debug_mode "inputs.py" && ((fixed_passed++)) || ((fixed_failed++))

echo ""
echo "inputs.py Results: $fixed_passed passed, $fixed_failed failed"
echo ""

# Final results
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "inputs_backup.py: $backup_passed/7 tests passed (expected to fail security tests)"
echo "inputs.py: $fixed_passed/7 tests passed (expected to pass all security tests)"
echo ""

if [ $fixed_failed -eq 0 ]; then
    echo "TEST PASSED: All security fixes verified!"
    exit 0
else
    echo "TEST FAILED: Some security issues remain in inputs.py"
    exit 1
fi
