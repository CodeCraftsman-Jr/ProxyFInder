@echo off
REM Proxy Finder Batch Script for Windows
REM This script runs the Python proxy finder

echo.
echo ========================================
echo       PROXY FINDER - Windows Runner
echo ========================================
echo.

REM Check if Python is installed
C:\Users\vasa\AppData\Local\Programs\Python\Python310\python.exe --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Starting proxy finder...
echo.

REM Run the proxy finder
C:\Users\vasa\AppData\Local\Programs\Python\Python310\python.exe proxy_finder.py

echo.
echo ========================================
echo            EXECUTION COMPLETE
echo ========================================
echo.
echo Working proxies have been saved to the 'working_proxies' folder
echo.

pause
