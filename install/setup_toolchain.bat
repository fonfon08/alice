@echo off
setlocal EnableExtensions
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
cd /d "%ROOT%"
call "%ROOT%\install\windows.bat" toolchain > "%ROOT%\install-toolchain.log" 2>&1
if errorlevel 1 exit /b 1
exit /b 0
