@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
python "%~dp0install.py"
if %errorlevel% neq 0 (
    echo.
    echo Setup failed.
)
pause
