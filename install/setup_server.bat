@echo off
setlocal EnableExtensions
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
cd /d "%ROOT%"
set "LOG=%ROOT%\install-server.log"

echo [ALICE] Server setup %DATE% %TIME% > "%LOG%"
call "%ROOT%\install\windows.bat" server >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [ALICE] windows.bat server failed >> "%LOG%"
  exit /b 1
)

set "PY="
if exist "%ROOT%\.venv\Scripts\python.exe" set "PY=%ROOT%\.venv\Scripts\python.exe"
if not defined PY if exist "%ROOT%\server\.venv\Scripts\python.exe" set "PY=%ROOT%\server\.venv\Scripts\python.exe"
if not defined PY (
  echo [ALICE] venv python not found >> "%LOG%"
  exit /b 1
)

if not exist "%ROOT%\server\operator.key" (
  "%PY%" "%ROOT%\alice.py" server key add operator >> "%LOG%" 2>&1
  if errorlevel 1 (
    echo [ALICE] key generation failed >> "%LOG%"
    exit /b 1
  )
)

echo [ALICE] Server setup complete >> "%LOG%"
exit /b 0
