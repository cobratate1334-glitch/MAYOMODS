@echo off
setlocal
cd /d "%~dp0"
REM Only applies to this PowerShell process; does not modify system settings.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Collect_BlueStacks_Crash.ps1"
echo.
echo Press any key to close the crash logger.
pause >nul
