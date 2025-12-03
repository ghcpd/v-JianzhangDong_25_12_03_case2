# Security Audit and Remediation Report

## 🔒 Overview

This repository contains the security audit and remediation of a Flask application with multiple critical vulnerabilities. The project includes the original vulnerable code, fixed secure code, comprehensive test suites, and deployment configurations.

## 📁 Generated Files

### Core Files
- **`inputs.py`** - The secure, fixed version of the application with all vulnerabilities addressed
- **`inputs_backup.py`** - Backup of the original vulnerable code for comparison and testing
- **`report.json`** - Detailed vulnerability report with severity ratings and fix explanations

### Environment Setup Files
- **`requirements.txt`** - Python dependencies (Flask, requests, PyYAML)
- **`Dockerfile`** - Docker container configuration for deployment
- **`setup.sh`** - Environment setup script for Linux/macOS

### Test Scripts
- **`run_test.sh`** - Security test script for Linux/macOS
- **`run_test.bat`** - Security test script for Windows
- **`auto_test.py`** - Automated test runner with environment detection

### Documentation
- **`README.md`** - This comprehensive guide

## 🛡️ Vulnerabilities Identified and Fixed

### Summary
- **Total Vulnerabilities:** 7
- **Critical:** 3
- **High:** 3
- **Medium:** 1

### Critical Vulnerabilities

1. **Hardcoded Secrets (Lines 11-13)**
   - **Risk:** Exposed credentials in source code
   - **Fix:** Replaced with environment variables using `os.environ.get()`

2. **SQL Injection (Line 27)**
   - **Risk:** Arbitrary SQL command execution
   - **Fix:** Implemented parameterized queries with input validation

3. **Command Injection (Line 52)**
   - **Risk:** Arbitrary system command execution
   - **Fix:** Used `shell=False` with list arguments and strict input validation

### High Vulnerabilities

4. **Weak Cryptography (Line 19)**
   - **Risk:** MD5 hash collisions and attacks
   - **Fix:** Upgraded to SHA-256 hashing algorithm

5. **Server-Side Request Forgery/SSRF (Line 38)**
   - **Risk:** Unauthorized internal/external requests
   - **Fix:** URL validation against whitelist with timeout protection

6. **Path Traversal (Lines 44-45)**
   - **Risk:** Arbitrary file read access
   - **Fix:** Path normalization and directory restriction

### Medium Vulnerabilities

7. **Debug Mode Enabled (Line 87)**
   - **Risk:** Exposure of sensitive debugging information
   - **Fix:** Made configurable via environment variable (default: False)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- For Docker: Docker installed and running

### Option 1: Local Setup (Linux/macOS)

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Run the secure application
python inputs.py
```

### Option 2: Local Setup (Windows)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir configs, logs -Force

# Set environment variables
$env:PAYMENT_TOKEN="test_token_123"
$env:MAIL_SERVER_KEY="test_mail_key_456"
$env:INTERNAL_AUTH="test_auth_789"
$env:ALLOWED_DOMAINS="localhost,127.0.0.1"
$env:ALLOWED_CONFIG_DIR="./configs"
$env:FLASK_DEBUG="False"

# Run the secure application
python inputs.py
```

### Option 3: Docker Setup

```bash
# Build Docker image
docker build -t secure-flask-app .

# Run container with environment variables
docker run -p 5000:5000 \
  -e PAYMENT_TOKEN="your_token" \
  -e MAIL_SERVER_KEY="your_key" \
  -e INTERNAL_AUTH="your_auth" \
  secure-flask-app
```

## 🧪 Running Security Tests

### Manual Testing

#### Linux/macOS
```bash
# Make test script executable
chmod +x run_test.sh

# Run tests
./run_test.sh
```

#### Windows
```cmd
# Run tests
run_test.bat
```

### Automated Testing

The `auto_test.py` script automatically detects your environment and runs the appropriate test script:

```bash
# Run automated tests
python auto_test.py
```

**Features:**
- ✅ Automatic environment detection (Windows/Linux/macOS/Docker)
- ✅ Runs platform-specific test scripts
- ✅ Timestamps all test output
- ✅ Logs results to `logs/test_run.log`
- ✅ Returns clear `TEST PASSED` or `TEST FAILED` status
- ✅ Proper exit codes for CI/CD integration

### Test Coverage

The test scripts verify all 7 security fixes:

1. ✅ SQL Injection Protection
2. ✅ Command Injection Protection
3. ✅ Hardcoded Secrets Removal
4. ✅ Strong Cryptography (SHA-256)
5. ✅ SSRF Protection
6. ✅ Path Traversal Protection
7. ✅ Debug Mode Configuration

## 📊 Checking Test Results

### View Logs

```bash
# View full log file
cat logs/test_run.log

# View last 50 lines (Linux/macOS)
tail -n 50 logs/test_run.log

# View last 50 lines (Windows PowerShell)
Get-Content logs/test_run.log -Tail 50
```

### Interpret Results

The log file contains:
- **Timestamp** for each log entry
- **Test execution output** from the test scripts
- **Individual test results** (PASS/FAIL for each vulnerability)
- **Final status line**: Either `TEST PASSED` or `TEST FAILED`

**Example Success Output:**
```
[2025-12-03 10:30:45] Overall Status: TEST PASSED
```

**Example Failure Output:**
```
[2025-12-03 10:30:45] Overall Status: TEST FAILED
```

### Exit Codes

- **Exit Code 0**: All tests passed
- **Exit Code 1**: One or more tests failed

This makes `auto_test.py` suitable for CI/CD pipelines:

```bash
# CI/CD integration example
python auto_test.py
if [ $? -eq 0 ]; then
    echo "Security tests passed - deploying..."
else
    echo "Security tests failed - blocking deployment"
    exit 1
fi
```

## 🔧 Configuration

### Environment Variables

Set these environment variables before running the application:

| Variable | Description | Example |
|----------|-------------|---------|
| `PAYMENT_TOKEN` | Payment service authentication token | `tok_prod_xxxxx` |
| `MAIL_SERVER_KEY` | Mail server API key | `mail_key_xxxxx` |
| `INTERNAL_AUTH` | Internal authentication secret | `secure_secret_xxxxx` |
| `ALLOWED_DOMAINS` | Comma-separated list of allowed domains for SSRF protection | `localhost,api.example.com` |
| `ALLOWED_CONFIG_DIR` | Base directory for configuration files | `./configs` |
| `FLASK_DEBUG` | Enable Flask debug mode (True/False) | `False` |

### Security Best Practices

1. **Never commit secrets to version control**
   - Use environment variables or secret management services
   - Add `.env` files to `.gitignore`

2. **Keep dependencies updated**
   - Regularly update `requirements.txt` dependencies
   - Monitor security advisories

3. **Use HTTPS in production**
   - Configure SSL/TLS certificates
   - Use a reverse proxy (nginx, Apache)

4. **Enable additional security headers**
   - Consider using Flask-Talisman for security headers
   - Implement CORS policies

5. **Regular security audits**
   - Run automated tests regularly
   - Perform code reviews
   - Use static analysis tools (bandit, safety)

## 📖 API Endpoints

### POST /auth
Authenticate user and receive token.

**Request:**
```json
{
  "username": "user123"
}
```

**Response:**
```json
{
  "token": "hashed_token"
}
```

### GET /profile?id=user_id
Retrieve user profile information.

**Response:**
```json
[
  [1, "John Doe", 1000.00]
]
```

### POST /transfer
Transfer funds to target account.

**Request:**
```json
{
  "target": "account123",
  "amount": 100.00,
  "notify_url": "http://localhost:5000/callback"
}
```

### POST /config
Load configuration from file.

**Request:**
```json
{
  "file": "config.yaml"
}
```

### GET /export?name=backup_name
Export data to zip file.

**Response:**
```json
{
  "ok": 1
}
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t secure-flask-app .

# Run with environment variables
docker run -d \
  -p 5000:5000 \
  -e PAYMENT_TOKEN="your_secure_token" \
  -e MAIL_SERVER_KEY="your_secure_key" \
  -e INTERNAL_AUTH="your_secure_auth" \
  -e ALLOWED_DOMAINS="localhost,trusted-domain.com" \
  --name flask-app \
  secure-flask-app
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - PAYMENT_TOKEN=${PAYMENT_TOKEN}
      - MAIL_SERVER_KEY=${MAIL_SERVER_KEY}
      - INTERNAL_AUTH=${INTERNAL_AUTH}
      - ALLOWED_DOMAINS=localhost,127.0.0.1
      - ALLOWED_CONFIG_DIR=/app/configs
      - FLASK_DEBUG=False
    volumes:
      - ./configs:/app/configs
      - ./logs:/app/logs
```

Run with:
```bash
docker-compose up -d
```

## 🔍 Comparing Vulnerable vs Secure Code

### View Differences

```bash
# Using diff (Linux/macOS)
diff inputs_backup.py inputs.py

# Using git diff
git diff --no-index inputs_backup.py inputs.py

# Using PowerShell (Windows)
Compare-Object (Get-Content inputs_backup.py) (Get-Content inputs.py)
```

### Key Changes Summary

| Vulnerability | Before | After |
|--------------|--------|-------|
| Secrets | Hardcoded strings | `os.environ.get()` |
| SQL Query | String formatting `%s` | Parameterized `?` placeholder |
| Subprocess | `shell=True` | `shell=False` with validation |
| Hashing | `hashlib.md5()` | `hashlib.sha256()` |
| HTTP Request | No validation | URL whitelist + timeout |
| File Access | Direct path | Path normalization + restriction |
| Debug Mode | `debug=True` | Configurable via env var |

## 📚 Additional Resources

### Security Tools
- **Bandit** - Python security linter: `pip install bandit && bandit -r inputs.py`
- **Safety** - Dependency vulnerability scanner: `pip install safety && safety check`
- **OWASP ZAP** - Web application security scanner

### Further Reading
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Python Security Documentation](https://docs.python.org/3/library/security_warnings.html)

## 📝 Report Details

For detailed information about each vulnerability, including:
- Exact line numbers
- Severity ratings
- Detailed descriptions
- Fix explanations
- Secure code snippets

Please refer to **`report.json`** for the complete structured report.

## 🤝 Support

If you encounter any issues:
1. Check the logs in `logs/test_run.log`
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check Python version (3.8+ required)

## ⚠️ Important Notes

- **`inputs_backup.py`** contains the original vulnerable code and should **NEVER** be deployed
- Always use **`inputs.py`** for production deployments
- Keep secrets secure and never commit them to version control
- Regularly run security tests, especially after code changes
- Review the `report.json` file for detailed security analysis

## 📄 License

This security audit and remediation project is provided as-is for educational and security improvement purposes.

---

**Last Updated:** December 3, 2025  
**Security Audit Completed:** ✅  
**All Vulnerabilities Fixed:** ✅  
**Tests Created:** ✅  
**Documentation Complete:** ✅
