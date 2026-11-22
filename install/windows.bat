@echo off
setlocal EnableExtensions

REM Copyright (C) 2026 Gustavo Henrique T.
REM SPDX-License-Identifier: GPL-3.0-or-later
REM See LICENSE in the repository root.

REM ======================================================================================
REM MAIN ENTRYPOINT
REM ======================================================================================

set "ROOT=%~dp0.."
set "MODE=%~1"
if "%MODE%"=="" set "MODE=all"

if /I "%MODE%"=="all" goto all
if /I "%MODE%"=="server" goto server
if /I "%MODE%"=="client" goto client
if /I "%MODE%"=="client-dist" goto client_dist
if /I "%MODE%"=="toolchain" goto toolchain
if /I "%MODE%"=="help" goto usage
if /I "%MODE%"=="--help" goto usage

:usage
echo Usage: windows.bat [all^|server^|client^|client-dist^|toolchain]
echo   all          Server venv + dependencies, client build, implant toolchain
echo   server       Server venv + python dependencies
echo   client       Client npm dependencies + electron-vite build
echo   client-dist  Client installer (electron-builder, needs client built)
echo   toolchain    Nim + MinGW-w64 for building Windows implants
exit /b 1

REM ======================================================================================
REM ALL
REM ======================================================================================

:all
call :ensure_python
if errorlevel 1 exit /b 1
call :install_server
if errorlevel 1 exit /b 1
call :install_client
if errorlevel 1 exit /b 1
call :install_toolchain
if errorlevel 1 exit /b 1
echo.
echo All done.
echo   server start:  python alice.py server start
echo   client start:  python alice.py client start
exit /b 0

REM ======================================================================================
REM SERVER
REM ======================================================================================

:server
call :ensure_python
if errorlevel 1 exit /b 1
call :install_server
if errorlevel 1 exit /b 1
echo Done. Start with: python alice.py server start
exit /b 0

:install_server
echo.
echo [server] Creating virtualenv...
if exist "%ROOT%\.venv\Scripts\python.exe" (
  set "SERVER_PY=%ROOT%\.venv\Scripts\python.exe"
) else (
  if not exist "%ROOT%\server\.venv\Scripts\python.exe" (
    "%PYTHON%" -m venv "%ROOT%\server\.venv"
    if errorlevel 1 exit /b 1
  )
  set "SERVER_PY=%ROOT%\server\.venv\Scripts\python.exe"
)
echo [server] Installing python dependencies...
"%SERVER_PY%" -m pip install --upgrade pip wheel setuptools
if errorlevel 1 exit /b 1
"%SERVER_PY%" -m pip install -r "%ROOT%\server\requirements.txt"
if errorlevel 1 exit /b 1
exit /b 0

REM ======================================================================================
REM CLIENT
REM ======================================================================================

:client
call :ensure_node
if errorlevel 1 exit /b 1
call :install_client
if errorlevel 1 exit /b 1
echo Done. Start with: python alice.py client start
exit /b 0

:client_dist
call :ensure_node
if errorlevel 1 exit /b 1
pushd "%ROOT%\client\gui"
if not exist node_modules (
  call npm ci --no-audit --no-fund
  if errorlevel 1 ( popd & exit /b 1 )
)
call npm run dist
if errorlevel 1 ( popd & exit /b 1 )
popd
call :shortcut
if errorlevel 1 exit /b 1
echo Done.
exit /b 0

:install_client
echo.
echo [client] Installing npm packages...
pushd "%ROOT%\client\gui"
if exist package-lock.json (
  call npm ci --no-audit --no-fund
) else (
  call npm install --no-audit --no-fund
)
if errorlevel 1 ( popd & exit /b 1 )
echo [client] Building...
call npm run build
if errorlevel 1 ( popd & exit /b 1 )
popd
exit /b 0

:shortcut
set "APP_EXE=%ROOT%\client\gui\dist\win-unpacked\ALICE.exe"
if not exist "%APP_EXE%" set "APP_EXE=%ROOT%\client\gui\dist\win-unpacked\alice.exe"
if not exist "%APP_EXE%" (
  echo No Windows build in "%ROOT%\client\gui\dist". 1>&2
  exit /b 1
)
set "ICO=%ROOT%\client\gui\public\icon.ico"
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ALICE.lnk"
set "ALICE_APP_EXE=%APP_EXE%"
set "ALICE_ICO=%ICO%"
set "ALICE_SHORTCUT=%SHORTCUT%"
set "ALICE_WORKDIR=%ROOT%\client\gui\dist\win-unpacked"
powershell -NoProfile -Command "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:ALICE_SHORTCUT); $s.TargetPath = $env:ALICE_APP_EXE; $s.WorkingDirectory = $env:ALICE_WORKDIR; if (Test-Path -LiteralPath $env:ALICE_ICO) { $s.IconLocation = $env:ALICE_ICO }; $s.Description = 'ALICE'; $s.Save()"
if errorlevel 1 exit /b 1
exit /b 0

REM ======================================================================================
REM TOOLCHAIN (Nim + MinGW-w64 for Windows implants)
REM ======================================================================================

:toolchain
call :install_toolchain
if errorlevel 1 exit /b 1
echo Done.
exit /b 0

:install_toolchain
echo.
echo [toolchain] Checking Nim and MinGW-w64...
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\install\toolchain.ps1" -Root "%ROOT%"
if errorlevel 1 exit /b 1
exit /b 0

REM ======================================================================================
REM PREREQUISITES
REM ======================================================================================

:ensure_python
echo.
echo [python] Checking...
set "PYTHON="
python -c "import sys" >nul 2>&1
if not errorlevel 1 (
  for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON=%%P"
)
if not defined PYTHON (
  py -3 -c "import sys" >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON=%%P"
  )
)
if not defined PYTHON (
  echo Python 3 was not found. Install it from https://www.python.org/downloads/windows/ and run again. 1>&2
  exit /b 1
)
echo [python] Using "%PYTHON%".
exit /b 0

:ensure_node
echo.
echo [node] Checking...
where node >nul 2>&1
if errorlevel 1 (
  echo Node.js was not found. Install it from https://nodejs.org/ and run again. 1>&2
  exit /b 1
)
where npm >nul 2>&1
if errorlevel 1 (
  echo npm was not found. Install Node.js from https://nodejs.org/ and run again. 1>&2
  exit /b 1
)
echo [node] Found.
exit /b 0
