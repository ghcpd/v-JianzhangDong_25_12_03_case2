@echo off
REM Test script for Windows
REM This script runs security tests on both the vulnerable and fixed versions

setlocal enabledelayedexpansion

echo ==========================================
echo Running Security Tests
echo ==========================================
echo.

REM Set environment variables for testing
set PAYMENT_TOKEN=test_token_123
set MAIL_SERVER_KEY=test_mail_key_456
set INTERNAL_AUTH=test_auth_789
set ALLOWED_DOMAINS=localhost,127.0.0.1
set ALLOWED_CONFIG_DIR=./configs
set FLASK_DEBUG=False

set backup_passed=0
set backup_failed=0
set fixed_passed=0
set fixed_failed=0

REM Function to test SQL injection vulnerability
echo ==========================================
echo Testing inputs_backup.py (Vulnerable Version)
echo ==========================================
echo.

echo Testing SQL Injection in inputs_backup.py...
findstr /C:"execute(q, (uid,))" inputs_backup.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Using parameterized queries
    set /a backup_passed+=1
) else (
    findstr /C:"\"SELECT.*%%s\".*%%.*uid" inputs_backup.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] SQL Injection vulnerability detected ^(string formatting^)
        set /a backup_failed+=1
    ) else (
        echo   [FAIL] Could not determine query method
        set /a backup_failed+=1
    )
)

echo Testing Command Injection in inputs_backup.py...
findstr /C:"shell=False" inputs_backup.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Using safe subprocess call ^(shell=False^)
    set /a backup_passed+=1
) else (
    findstr /C:"shell=True" inputs_backup.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] Command Injection vulnerability detected ^(shell=True^)
        set /a backup_failed+=1
    ) else (
        echo   [FAIL] Could not determine subprocess method
        set /a backup_failed+=1
    )
)

echo Testing for Hardcoded Secrets in inputs_backup.py...
findstr /C:"os.environ.get(\"PAYMENT_TOKEN\"" inputs_backup.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Using environment variables for secrets
    set /a backup_passed+=1
) else (
    findstr /C:"PAYMENT_TOKEN = \"tok_" inputs_backup.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] Hardcoded secrets detected
        set /a backup_failed+=1
    ) else (
        echo   [FAIL] Could not determine secret storage method
        set /a backup_failed+=1
    )
)

echo Testing for Weak Cryptography in inputs_backup.py...
findstr /C:"hashlib.sha256" inputs_backup.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Using SHA-256 for hashing
    set /a backup_passed+=1
) else (
    findstr /C:"hashlib.md5" inputs_backup.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] Weak cryptography detected ^(MD5^)
        set /a backup_failed+=1
    ) else (
        echo   [FAIL] Could not determine hash algorithm
        set /a backup_failed+=1
    )
)

echo Testing for SSRF Protection in inputs_backup.py...
findstr /C:"ALLOWED_DOMAINS" inputs_backup.py >nul 2>&1 && findstr /C:"urlparse" inputs_backup.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] SSRF protection implemented
    set /a backup_passed+=1
) else (
    findstr /C:"requests.post(url" inputs_backup.py >nul 2>&1
    if !errorlevel! equ 0 (
        findstr /C:"urlparse" inputs_backup.py >nul 2>&1
        if !errorlevel! neq 0 (
            echo   [FAIL] SSRF vulnerability detected ^(no URL validation^)
            set /a backup_failed+=1
        ) else (
            echo   [FAIL] Could not determine SSRF protection
            set /a backup_failed+=1
        )
    ) else (
        echo   [FAIL] Could not determine SSRF protection
        set /a backup_failed+=1
    )
)

echo Testing for Path Traversal Protection in inputs_backup.py...
findstr /C:"os.path.abspath" inputs_backup.py >nul 2>&1 && findstr /C:"startswith(base_dir)" inputs_backup.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Path traversal protection implemented
    set /a backup_passed+=1
) else (
    echo   [FAIL] Path traversal vulnerability detected
    set /a backup_failed+=1
)

echo Testing Debug Mode Configuration in inputs_backup.py...
findstr /C:"os.environ.get(\"FLASK_DEBUG\"" inputs_backup.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Debug mode is configurable via environment
    set /a backup_passed+=1
) else (
    findstr /C:"app.run(debug=True)" inputs_backup.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] Debug mode hardcoded to True
        set /a backup_failed+=1
    ) else (
        echo   [FAIL] Could not determine debug mode configuration
        set /a backup_failed+=1
    )
)

echo.
echo inputs_backup.py Results: !backup_passed! passed, !backup_failed! failed
echo.

REM Test fixed version
echo ==========================================
echo Testing inputs.py (Fixed Version)
echo ==========================================
echo.

echo Testing SQL Injection in inputs.py...
findstr /C:"execute(q, (uid,))" inputs.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Using parameterized queries
    set /a fixed_passed+=1
) else (
    findstr /C:"\"SELECT.*%%s\".*%%.*uid" inputs.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] SQL Injection vulnerability detected ^(string formatting^)
        set /a fixed_failed+=1
    ) else (
        echo   [FAIL] Could not determine query method
        set /a fixed_failed+=1
    )
)

echo Testing Command Injection in inputs.py...
findstr /C:"shell=False" inputs.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Using safe subprocess call ^(shell=False^)
    set /a fixed_passed+=1
) else (
    findstr /C:"shell=True" inputs.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] Command Injection vulnerability detected ^(shell=True^)
        set /a fixed_failed+=1
    ) else (
        echo   [FAIL] Could not determine subprocess method
        set /a fixed_failed+=1
    )
)

echo Testing for Hardcoded Secrets in inputs.py...
findstr /C:"os.environ.get(\"PAYMENT_TOKEN\"" inputs.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Using environment variables for secrets
    set /a fixed_passed+=1
) else (
    findstr /C:"PAYMENT_TOKEN = \"tok_" inputs.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] Hardcoded secrets detected
        set /a fixed_failed+=1
    ) else (
        echo   [FAIL] Could not determine secret storage method
        set /a fixed_failed+=1
    )
)

echo Testing for Weak Cryptography in inputs.py...
findstr /C:"hashlib.sha256" inputs.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Using SHA-256 for hashing
    set /a fixed_passed+=1
) else (
    findstr /C:"hashlib.md5" inputs.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] Weak cryptography detected ^(MD5^)
        set /a fixed_failed+=1
    ) else (
        echo   [FAIL] Could not determine hash algorithm
        set /a fixed_failed+=1
    )
)

echo Testing for SSRF Protection in inputs.py...
findstr /C:"ALLOWED_DOMAINS" inputs.py >nul 2>&1 && findstr /C:"urlparse" inputs.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] SSRF protection implemented
    set /a fixed_passed+=1
) else (
    findstr /C:"requests.post(url" inputs.py >nul 2>&1
    if !errorlevel! equ 0 (
        findstr /C:"urlparse" inputs.py >nul 2>&1
        if !errorlevel! neq 0 (
            echo   [FAIL] SSRF vulnerability detected ^(no URL validation^)
            set /a fixed_failed+=1
        ) else (
            echo   [FAIL] Could not determine SSRF protection
            set /a fixed_failed+=1
        )
    ) else (
        echo   [FAIL] Could not determine SSRF protection
        set /a fixed_failed+=1
    )
)

echo Testing for Path Traversal Protection in inputs.py...
findstr /C:"os.path.abspath" inputs.py >nul 2>&1 && findstr /C:"startswith(base_dir)" inputs.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Path traversal protection implemented
    set /a fixed_passed+=1
) else (
    echo   [FAIL] Path traversal vulnerability detected
    set /a fixed_failed+=1
)

echo Testing Debug Mode Configuration in inputs.py...
findstr /C:"os.environ.get(\"FLASK_DEBUG\"" inputs.py >nul 2>&1
if !errorlevel! equ 0 (
    echo   [PASS] Debug mode is configurable via environment
    set /a fixed_passed+=1
) else (
    findstr /C:"app.run(debug=True)" inputs.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [FAIL] Debug mode hardcoded to True
        set /a fixed_failed+=1
    ) else (
        echo   [FAIL] Could not determine debug mode configuration
        set /a fixed_failed+=1
    )
)

echo.
echo inputs.py Results: !fixed_passed! passed, !fixed_failed! failed
echo.

REM Final results
echo ==========================================
echo Test Summary
echo ==========================================
echo inputs_backup.py: !backup_passed!/7 tests passed (expected to fail security tests)
echo inputs.py: !fixed_passed!/7 tests passed (expected to pass all security tests)
echo.

if !fixed_failed! equ 0 (
    echo TEST PASSED: All security fixes verified!
    exit /b 0
) else (
    echo TEST FAILED: Some security issues remain in inputs.py
    exit /b 1
)
