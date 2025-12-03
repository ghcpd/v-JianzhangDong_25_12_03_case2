@echo off
if "%1"=="" (
  echo Usage: run_test.bat ^<file^
  exit /b 2
)
python test_inputs.py %1
