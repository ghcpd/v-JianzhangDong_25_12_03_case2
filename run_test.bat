@echo off
setlocal enabledelayedexpansion
if not exist logs mkdir logs
set SUMMARY_LOG=logs\test_run.log
break> %SUMMARY_LOG%

if exist .venv\Scripts\python.exe (
  set PYTHON_CMD=.venv\Scripts\python.exe
) else (
  set PYTHON_CMD=python
)

%PYTHON_CMD% run_tests.py
set rc=!ERRORLEVEL!
echo [%DATE% %TIME%] run_tests exit=!rc! >> %SUMMARY_LOG%
if !rc! EQU 0 (
  echo TEST PASSED >> %SUMMARY_LOG%
  exit /b 0
) else (
  echo TEST FAILED >> %SUMMARY_LOG%
  exit /b 1
)
