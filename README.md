# Flask Security Audit Report

## Overview

This repository contains a comprehensive security audit of a Flask application vulnerable to multiple critical security issues. The audit includes identification of vulnerabilities, detailed fixes, and automated testing infrastructure.

## Files Generated

### Core Application Files
- **`inputs.py`** - Secured version of the Flask application with all vulnerabilities fixed
- **`inputs_backup.py`** - Original backup of the vulnerable code for comparison
- **`requirements.txt`** - Python dependencies required for the application

### Security Documentation
- **`report.json`** - Detailed vulnerability report with severity levels, descriptions, and fixes
- **`README.md`** - This file, containing setup and usage instructions

### Environment Setup Files
- **`Dockerfile`** - Docker container configuration for reproducible environment
- **`setup.sh`** - Setup script for Linux/macOS environments
- **`run_test.sh`** - Test script for Linux/macOS platforms
- **`run_test.bat`** - Test script for Windows platform

### Testing & Automation
- **`auto_test.py`** - Automatic environment detection and test execution script
- **`logs/test_run.log`** - Test execution logs (created during runtime)

## Vulnerabilities Fixed

| ID | Type | Severity | Lines | Status |
|----|------|----------|-------|--------|
| 1 | Hardcoded Secrets | Critical | 12-14 | ✓ Fixed |
| 2 | SQL Injection | Critical | 28 | ✓ Fixed |
| 3 | Weak Hashing | High | 22 | ✓ Fixed |
| 4 | Command Injection | Critical | 48 | ✓ Fixed |
| 5 | Path Traversal | High | 43 | ✓ Fixed |
| 6 | Debug Mode Enabled | High | 83 | ✓ Fixed |
| 7 | SSRF Vulnerability | High | 38 | ✓ Fixed |
| 8 | Sensitive Data Exposure | Medium | 37 | ✓ Fixed |

**Total: 8 vulnerabilities (3 Critical, 3 High, 2 Medium)**

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip package manager
- Git (optional)

### Linux/macOS Setup

#### Method 1: Using setup.sh Script
```bash
# Navigate to the project directory
cd /path/to/project

# Make setup script executable
chmod +x setup.sh

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

#### Method 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs
```

### Windows Setup

#### Method 1: Using Command Prompt
```batch
# Navigate to the project directory
cd C:\path\to\project

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir logs
```

#### Method 2: Using PowerShell
```powershell
# Navigate to the project directory
cd C:\path\to\project

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create logs directory
New-Item -ItemType Directory -Force -Path logs
```

### Docker Setup

#### Build Docker Image
```bash
# Build the Docker image
docker build -t flask-security-audit .

# Run container
docker run -it -p 5000:5000 flask-security-audit
```

## Running Tests

### Linux/macOS Test Execution

#### Using the run_test.sh Script
```bash
# Make script executable
chmod +x run_test.sh

# Run tests
./run_test.sh
```

### Windows Test Execution

#### Using the run_test.bat Script
```batch
# Run tests
run_test.bat
```

### Automatic Environment Detection (All Platforms)

The `auto_test.py` script automatically detects your environment and runs the appropriate tests:

```bash
# Python (works on all platforms)
python auto_test.py
```

The script will:
1. Detect the current environment (Windows/Linux/Docker)
2. Run the appropriate test script
3. Log all output to `logs/test_run.log`
4. Print final status: **TEST PASSED** or **TEST FAILED**

### Test Output

The test script validates:
1. **Syntax Check** - Ensures both versions compile correctly
2. **Import Test** - Verifies modules can be imported
3. **Vulnerability Scan** - Confirms vulnerabilities in backup version
4. **Fix Verification** - Verifies all fixes are present in secure version

## Checking Test Logs

### View Real-time Logs
```bash
# Linux/macOS
tail -f logs/test_run.log

# Windows PowerShell
Get-Content logs/test_run.log -Tail 50 -Wait
```

### Parse Log Results
The log file contains:
- **Timestamp** - When each test ran
- **Detailed Output** - Full test output and results
- **Final Status** - `TEST PASSED` or `TEST FAILED` line at the end

### Example Log Entry
```
2025-12-03 10:15:30,123 - INFO - Executing: run_test.sh
2025-12-03 10:15:30,456 - INFO - STDOUT:
1. Running syntax check...
2. Testing imports...
✓ Secure version imports successfully
✓ Hardcoded secret found in backup (expected)
✓ SQL injection vulnerability found in backup (expected)
...
2025-12-03 10:15:35,789 - INFO - TEST PASSED
```

## Vulnerability Details

For detailed information about each vulnerability, fix, and severity assessment, refer to **`report.json`**.

### Report Format
```json
{
  "summary": {
    "total_vulnerabilities": 8,
    "critical": 3,
    "high": 3,
    "medium": 2,
    "low": 0
  },
  "details": [
    {
      "id": 1,
      "file": "inputs.py",
      "line_numbers": [12, 13, 14],
      "vulnerability_type": "Hardcoded Secrets",
      "severity": "Critical",
      "description": "...",
      "fix_explanation": "...",
      "secure_code_snippet": "..."
    }
  ]
}
```

### Quick Reference: What Was Fixed

**Critical Issues Fixed:**
1. **Hardcoded API tokens** → Moved to environment variables
2. **SQL injection via user input** → Using parameterized queries
3. **OS command injection** → Using zipfile API instead of shell commands

**High-Severity Issues Fixed:**
1. **Weak MD5 password hashing** → Using bcrypt
2. **Path traversal vulnerability** → Path validation and sandboxing
3. **Debug mode enabled in production** → Controlled via environment variable
4. **SSRF vulnerability** → URL validation against private IP ranges

**Medium-Severity Issues Fixed:**
1. **Sensitive data logging** → Replaced print() with secure logging

## Running the Application

### Development Mode (Linux/macOS)
```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PAYMENT_TOKEN="your_token"
export MAIL_SERVER_KEY="your_key"
export INTERNAL_AUTH="your_auth"
export FLASK_DEBUG=False

# Run the application
python inputs.py
```

### Development Mode (Windows)
```batch
# Activate virtual environment
venv\Scripts\activate.bat

# Set environment variables
set PAYMENT_TOKEN=your_token
set MAIL_SERVER_KEY=your_key
set INTERNAL_AUTH=your_auth
set FLASK_DEBUG=False

# Run the application
python inputs.py
```

### Using Docker
```bash
# Build and run
docker build -t flask-security-audit .
docker run -e PAYMENT_TOKEN="your_token" -e MAIL_SERVER_KEY="your_key" -e INTERNAL_AUTH="your_auth" -p 5000:5000 flask-security-audit
```

## Comparing Vulnerable vs Secure Versions

To review the differences between the vulnerable and secure versions:

```bash
# Linux/macOS
diff -u inputs_backup.py inputs.py

# Windows PowerShell
Compare-Object (Get-Content inputs_backup.py) (Get-Content inputs.py)
```

## Security Best Practices Applied

1. **Secrets Management** - All credentials moved to environment variables
2. **Input Validation** - All user inputs validated and sanitized
3. **Parameterized Queries** - SQL queries use parameters, not string concatenation
4. **Modern Cryptography** - Replaced MD5 with bcrypt for password hashing
5. **Command Execution Safety** - Avoided shell interpretation of user input
6. **SSRF Prevention** - Validated URLs against private IP ranges
7. **Error Handling** - Added try-catch blocks with secure error messages
8. **Logging** - Implemented structured logging without sensitive data exposure
9. **Debug Mode Control** - Debug mode disabled by default, controllable via environment

## Troubleshooting

### Issue: "Module not found" errors
**Solution:** Ensure requirements are installed:
```bash
pip install -r requirements.txt
```

### Issue: Permission denied on run_test.sh
**Solution:** Make script executable:
```bash
chmod +x run_test.sh
chmod +x setup.sh
chmod +x auto_test.py
```

### Issue: Tests failing on Windows
**Solution:** Ensure you're using run_test.bat or python auto_test.py, not run_test.sh

### Issue: Logs directory doesn't exist
**Solution:** auto_test.py creates it automatically. For manual creation:
```bash
mkdir logs  # Linux/macOS
mkdir logs  # Windows PowerShell/CMD
```

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Flask Security Guide](https://flask.palletsprojects.com/en/latest/security/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt)

## License

This security audit and test suite is provided for educational and security testing purposes.

---

**Last Updated:** December 3, 2025  
**Audit Severity:** 3 Critical, 3 High, 2 Medium vulnerabilities identified and fixed
