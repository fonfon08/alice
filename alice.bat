@echo off
setlocal
set "ROOT=%~dp0"
set "PY=python"
if exist "%ROOT%.venv\Scripts\python.exe" set "PY=%ROOT%.venv\Scripts\python.exe"
if exist "%ROOT%server\.venv\Scripts\python.exe" set "PY=%ROOT%server\.venv\Scripts\python.exe"
"%PY%" "%ROOT%alice.py" %*
