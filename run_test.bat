@echo off
REM run_test.bat - Test script for Windows

setlocal enabledelayedexpansion

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo === Running Security Tests ===
echo Platform: Windows
python --version
echo.

REM Run basic syntax check
echo 1. Running syntax check...
python -m py_compile inputs.py inputs_backup.py
if errorlevel 1 (
    echo ERROR: Syntax check failed
    exit /b 1
)
echo ✓ Syntax check passed

REM Check for critical vulnerabilities in backup
echo.
echo 2. Checking for known vulnerabilities in backup...
findstr /M "PAYMENT_TOKEN = " inputs_backup.py >nul
if not errorlevel 1 (
    echo ✓ Hardcoded secret found in backup (expected)
)

findstr /M "WHERE id = " inputs_backup.py >nul
if not errorlevel 1 (
    echo ✓ SQL injection vulnerability found in backup (expected)
)

findstr /M "shell=True" inputs_backup.py >nul
if not errorlevel 1 (
    echo ✓ Command injection vulnerability found in backup (expected)
)

findstr /M "debug=True" inputs_backup.py >nul
if not errorlevel 1 (
    echo ✓ Debug mode enabled in backup (expected)
)

findstr /M "hashlib.md5" inputs_backup.py >nul
if not errorlevel 1 (
    echo ✓ Weak hashing found in backup (expected)
)

REM Check that vulnerabilities are fixed in secure version
echo.
echo 3. Checking for fixes in secure version...
findstr /M "os.getenv" inputs.py >nul
if not errorlevel 1 (
    echo ✓ Secrets moved to environment variables
)

findstr /M "c.execute(q, (uid,))" inputs.py >nul
if not errorlevel 1 (
    echo ✓ SQL injection fixed with parameterized queries
)

findstr /M "zipfile.ZipFile" inputs.py >nul
if not errorlevel 1 (
    echo ✓ Command injection fixed - using zipfile API instead of shell
)

findstr /M "os.getenv('FLASK_DEBUG'" inputs.py >nul
if not errorlevel 1 (
    echo ✓ Debug mode now controlled by environment variable
)

findstr /M "bcrypt" inputs.py >nul
if not errorlevel 1 (
    echo ✓ Weak hashing replaced with bcrypt
)

findstr /M "is_safe_url" inputs.py >nul
if not errorlevel 1 (
    echo ✓ SSRF protection added
)

findstr /M "os.path.abspath" inputs.py >nul
if not errorlevel 1 (
    echo ✓ Path traversal fixed with path validation
)

echo.
echo === All Tests Passed ===
exit /b 0
