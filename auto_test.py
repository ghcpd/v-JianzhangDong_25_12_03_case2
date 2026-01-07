#!/usr/bin/env python3
"""
Automatic Test Execution Script
This script detects the current environment and runs the appropriate test script.
It logs all output with timestamps and determines test success/failure.
"""

import os
import sys
import platform
import subprocess
from datetime import datetime
from pathlib import Path


class AutoTest:
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_file = self.log_dir / "test_run.log"
        self.system = platform.system()
        
    def setup_logging(self):
        """Create logs directory if it doesn't exist"""
        self.log_dir.mkdir(exist_ok=True)
        
    def log_message(self, message, to_console=True):
        """Log message with timestamp to both console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if to_console:
            print(log_entry)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def detect_environment(self):
        """Detect the current operating environment"""
        self.log_message("=" * 60)
        self.log_message("Detecting Environment...")
        self.log_message("=" * 60)
        
        # Check if running in Docker
        if os.path.exists("/.dockerenv"):
            env = "Docker"
        elif self.system == "Linux":
            env = "Linux"
        elif self.system == "Darwin":
            env = "macOS"
        elif self.system == "Windows":
            env = "Windows"
        else:
            env = "Unknown"
        
        self.log_message(f"Detected Environment: {env}")
        self.log_message(f"Platform: {platform.platform()}")
        self.log_message(f"Python Version: {sys.version}")
        self.log_message("")
        
        return env
    
    def run_test_script(self, script_name, script_path):
        """Run a test script and capture output"""
        self.log_message("=" * 60)
        self.log_message(f"Running: {script_name}")
        self.log_message("=" * 60)
        self.log_message("")
        
        try:
            # Determine the command based on file extension
            if script_path.endswith(".sh"):
                # For bash scripts on Linux/macOS
                if self.system in ["Linux", "Darwin"]:
                    cmd = ["bash", script_path]
                else:
                    self.log_message(f"ERROR: Cannot run .sh script on {self.system}")
                    return False
            elif script_path.endswith(".bat"):
                # For batch scripts on Windows
                if self.system == "Windows":
                    cmd = [script_path]
                else:
                    self.log_message(f"ERROR: Cannot run .bat script on {self.system}")
                    return False
            else:
                self.log_message(f"ERROR: Unknown script type: {script_path}")
                return False
            
            # Run the command and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output line by line
            for line in process.stdout:
                line = line.rstrip()
                self.log_message(line)
            
            # Wait for process to complete
            process.wait()
            exit_code = process.returncode
            
            self.log_message("")
            self.log_message(f"Script Exit Code: {exit_code}")
            
            # Determine test status
            if exit_code == 0:
                self.log_message("TEST PASSED")
                return True
            else:
                self.log_message("TEST FAILED")
                return False
                
        except FileNotFoundError:
            self.log_message(f"ERROR: Test script not found: {script_path}")
            self.log_message("TEST FAILED")
            return False
        except Exception as e:
            self.log_message(f"ERROR: Exception occurred: {str(e)}")
            self.log_message("TEST FAILED")
            return False
        finally:
            self.log_message("")
    
    def run_all_tests(self):
        """Run all test scripts based on environment"""
        self.setup_logging()
        
        # Clear previous log
        if self.log_file.exists():
            self.log_file.unlink()
        
        self.log_message("=" * 60)
        self.log_message("AUTOMATED TEST EXECUTION")
        self.log_message("=" * 60)
        self.log_message("")
        
        # Detect environment
        env = self.detect_environment()
        
        # Determine which test script to run
        if env in ["Linux", "macOS", "Docker"]:
            test_script = "run_test.sh"
        elif env == "Windows":
            test_script = "run_test.bat"
        else:
            self.log_message(f"ERROR: Unsupported environment: {env}")
            self.log_message("TEST FAILED")
            return False
        
        # Check if test script exists
        if not os.path.exists(test_script):
            self.log_message(f"ERROR: Test script not found: {test_script}")
            self.log_message("TEST FAILED")
            return False
        
        # Make script executable on Unix-like systems
        if env in ["Linux", "macOS", "Docker"] and test_script.endswith(".sh"):
            try:
                os.chmod(test_script, 0o755)
            except Exception as e:
                self.log_message(f"WARNING: Could not make script executable: {str(e)}")
        
        # Run the test script
        success = self.run_test_script(test_script, test_script)
        
        # Final summary
        self.log_message("=" * 60)
        self.log_message("FINAL SUMMARY")
        self.log_message("=" * 60)
        self.log_message(f"Environment: {env}")
        self.log_message(f"Test Script: {test_script}")
        self.log_message(f"Log File: {self.log_file}")
        
        if success:
            self.log_message("Overall Status: TEST PASSED")
            self.log_message("=" * 60)
            return True
        else:
            self.log_message("Overall Status: TEST FAILED")
            self.log_message("=" * 60)
            return False


def main():
    """Main entry point"""
    auto_test = AutoTest()
    success = auto_test.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
