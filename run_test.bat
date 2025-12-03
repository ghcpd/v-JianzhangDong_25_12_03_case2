@echo off
set MODULE=%1
if "%MODULE%"=="" set MODULE=inputs.py
python tests_runner.py --module "%MODULE%"
exit /b %ERRORLEVEL%
