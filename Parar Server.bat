@echo off
for %%I in ("%~dp0") do set "ROOT=%%~fI"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\install\stop_server.ps1"
