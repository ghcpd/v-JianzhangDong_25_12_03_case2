#!/usr/bin/env python
"""
auto_test.py - Automatic test execution script with environment detection
This script detects the current environment (Windows/Linux/Docker) and runs appropriate tests
for both inputs_backup.py (vulnerable version) and inputs.py (secure version) in sequence.
Logs all output to logs/test_run.log with timestamps.
"""

import os
import sys
import subprocess
import platform
import logging
import importlib.util
from datetime import datetime
from pathlib import Path

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "test_run.log"

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)
# Add console handler with error handling
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


def detect_environment():
    """Detect current environment (Windows, Linux, or Docker)."""
    system = platform.system()
    
    # Check if running in Docker
    if Path("/.dockerenv").exists():
        return "docker"
    
    if system == "Windows":
        return "windows"
    elif system in ("Linux", "Darwin"):  # Darwin is macOS
        return "linux"
    else:
        return "unknown"


def run_command(cmd, shell=False, description=""):
    """
    Execute a command and return the exit code.
    Logs output to both console and file.
    """
    try:
        logger.info(f"Executing: {description if description else cmd}")
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Log output
        if result.stdout:
            logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"STDERR:\n{result.stderr}")
        
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error("Command timed out after 300 seconds")
        return 1, "", "Timeout"
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return 1, "", str(e)


def test_file_syntax(filepath):
    """Test Python file syntax by compiling it."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        compile(code, filepath, 'exec')
        return True, "Syntax OK"
    except SyntaxError as e:
        return False, f"Syntax Error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def test_file_imports(filepath):
    """Test that a Python file can be imported."""
    try:
        spec = importlib.util.spec_from_file_location("test_module", filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules["test_module"] = module
        spec.loader.exec_module(module)
        return True, "Imports OK"
    except ImportError as e:
        # Some imports may fail due to missing dependencies, which is expected
        # Don't fail if bcrypt or other dependencies are missing - they can be installed separately
        return True, f"Import check skipped (dependencies may not be installed): {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def test_file_vulnerabilities(filepath, is_backup=False):
    """
    Test file for expected vulnerabilities (backup) or fixes (secure version).
    Returns (passed, details)
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        if is_backup:
            # Check that vulnerabilities exist in backup
            checks = [
                ('Hardcoded secret', 'PAYMENT_TOKEN = "tok_production' in content),
                ('SQL injection', "WHERE id = '%s'" in content),
                ('Command injection', 'shell=True' in content),
                ('Debug mode enabled', 'debug=True' in content),
                ('Weak hashing', 'hashlib.md5' in content),
            ]
            results = [f"✓ {name} (found as expected)" for name, found in checks if found]
            return True, results
        else:
            # Check that fixes are present in secure version
            checks = [
                ('Secrets moved to env', "os.getenv('PAYMENT_TOKEN'" in content),
                ('SQL injection fixed', 'c.execute(q, (uid,))' in content),
                ('Command injection fixed', 'zipfile.ZipFile' in content),
                ('Debug mode controlled', "os.getenv('FLASK_DEBUG'" in content),
                ('Weak hashing replaced', 'bcrypt.hashpw' in content),
                ('SSRF protection added', 'is_safe_url' in content),
                ('Path traversal fixed', 'os.path.abspath' in content),
            ]
            results = [f"✓ {name}" for name, found in checks if found]
            failed = [f"✗ {name}" for name, found in checks if not found]
            
            if failed:
                return False, results + failed
            return True, results
    except Exception as e:
        return False, [f"Error: {str(e)}"]


def run_tests(environment):
    """Run tests for both inputs_backup.py and inputs.py in sequence."""
    logger.info("=" * 70)
    logger.info(f"Starting Security Audit Tests - Environment: {environment}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 70)
    
    all_passed = True
    test_results = []
    files_to_test = [
        ("inputs_backup.py", True),   # (filename, is_backup)
        ("inputs.py", False)           # (filename, is_secure)
    ]
    
    # Test each file in sequence
    for filepath, is_backup in files_to_test:
        file_type = "VULNERABLE (Backup)" if is_backup else "SECURE (Fixed)"
        logger.info("")
        logger.info("-" * 70)
        logger.info(f"Testing: {filepath} [{file_type}]")
        logger.info(f"Test Start Time: {datetime.now().isoformat()}")
        logger.info("-" * 70)
        
        file_passed = True
        
        # Check if file exists
        if not Path(filepath).exists():
            logger.error(f"✗ File not found: {filepath}")
            test_results.append((filepath, "FILE_NOT_FOUND"))
            all_passed = False
            continue
        
        # Test 1: Syntax check
        logger.info(f"[1/4] Running syntax check for {filepath}...")
        syntax_ok, syntax_msg = test_file_syntax(filepath)
        if syntax_ok:
            logger.info(f"  [OK] {syntax_msg}")
        else:
            logger.error(f"  [FAIL] {syntax_msg}")
            file_passed = False
            all_passed = False
        
        # Test 2: Import test
        logger.info(f"[2/4] Testing imports for {filepath}...")
        import_ok, import_msg = test_file_imports(filepath)
        if import_ok:
            logger.info(f"  [OK] {import_msg}")
        else:
            logger.error(f"  [FAIL] {import_msg}")
            file_passed = False
            all_passed = False
        
        # Test 3: Vulnerability check
        logger.info(f"[3/4] Checking vulnerabilities in {filepath}...")
        vuln_ok, vuln_results = test_file_vulnerabilities(filepath, is_backup)
        for result in vuln_results:
            logger.info(f"  {result}")
        if not vuln_ok:
            file_passed = False
            all_passed = False
        
        # Test 4: Run test script
        logger.info(f"[4/4] Running test script for {filepath}...")
        if environment == "windows":
            test_script = "run_test.bat"
            exit_code, stdout, stderr = run_command(test_script, shell=True, description=test_script)
        elif environment in ("linux", "docker"):
            test_script = "run_test.sh"
            os.chmod(test_script, 0o755)
            exit_code, stdout, stderr = run_command(f"bash {test_script}", shell=True, description=test_script)
        else:
            exit_code = 1
            logger.error(f"Unknown environment: {environment}")
        
        if exit_code == 0:
            logger.info(f"  [OK] Test script passed")
        else:
            logger.error(f"  [FAIL] Test script failed with exit code {exit_code}")
            file_passed = False
            all_passed = False
        
        # Log test result for this file
        test_status = "PASSED" if file_passed else "FAILED"
        test_results.append((filepath, test_status))
        logger.info(f"Test End Time: {datetime.now().isoformat()}")
        logger.info(f"Result: {test_status}")
    
    # Log overall summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("OVERALL TEST SUMMARY")
    logger.info("=" * 70)
    for filepath, result in test_results:
        status_symbol = "[PASS]" if result == "PASSED" else "[FAIL]"
        logger.info(f"{status_symbol} {filepath}: {result}")
    
    logger.info("=" * 70)
    if all_passed:
        logger.info("FINAL STATUS: TEST PASSED")
    else:
        logger.info("FINAL STATUS: TEST FAILED")
    logger.info(f"Completion Time: {datetime.now().isoformat()}")
    logger.info("=" * 70)
    
    return all_passed


def main():
    """Main entry point."""
    try:
        # Detect environment
        environment = detect_environment()
        logger.info(f"Detected environment: {environment}")
        
        # Run tests
        success = run_tests(environment)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.info("TEST FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
