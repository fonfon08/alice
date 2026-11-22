@echo off
for %%I in ("%~dp0") do set "ROOT=%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\install\start_server.ps1"
if errorlevel 1 pause
