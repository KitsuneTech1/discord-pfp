@echo off
setlocal
echo ========================================================
echo   Profile Fetch (discord-pfp)
echo   Kitsune Technologies LLC
echo ========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python 3 was not found on your system.
    echo Please install Python 3.10+ from https://python.org/
    pause
    exit /b 1
)

python discord_pfp.py --help
pause
