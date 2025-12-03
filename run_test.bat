@echo off
setlocal ENABLEDELAYEDEXPANSION
set MODULE=%1
if "%MODULE%"=="" set MODULE=%MODULE_UNDER_TEST%
if "%MODULE%"=="" set MODULE=input
set MODULE_UNDER_TEST=%MODULE%
python -m pytest -q
set EXITCODE=%ERRORLEVEL%
endlocal & exit /b %EXITCODE%
