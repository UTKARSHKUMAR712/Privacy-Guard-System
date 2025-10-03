@echo off
title Privacy Guard System
color 0A
echo.
echo ===============================================
echo          Privacy Guard System v1.0
echo ===============================================
echo.
echo Starting Privacy Guard...
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from python.org
    pause
    exit /b 1
)

if not exist "privacy_guard.py" (
    echo ERROR: privacy_guard.py not found!
    echo Please run setup.py first
    pause
    exit /b 1
)

python privacy_guard.py --camera 1

if errorlevel 1 (
    echo.
    echo ===============================================
    echo An error occurred. Check the logs folder.
    echo ===============================================
    pause
) else (
    echo.
    echo ===============================================
    echo Privacy Guard stopped normally.
    echo ===============================================
    timeout /t 3 >nul
)
