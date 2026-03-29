@echo off
REM Engram Single-Command Entry Point
REM This script initializes the backend and launches the TUI environment.
REM Usage: .\engram.bat

setlocal
set PYTHONPATH=%~dp0

REM 1. Check if the venv exists and use its Python directly to avoid global version conflicts
if exist "%~dp0venv\Scripts\python.exe" (
    set PY_EXE="%~dp0venv\Scripts\python.exe"
    echo [INFO] Using Virtual Environment: %~dp0venv
) else (
    set PY_EXE=python
    echo [WARNING] Virtual environment NOT found at %~dp0venv. Using global python.
)

REM 2. Run the Engram CLI
%PY_EXE% "%~dp0app\cli.py" %*

REM 3. Error Handling
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Engram failed to start.
    echo.
    echo TIP: If you see "No module named pydantic_core", run these two commands to reset your environment to Python 3.12:
    echo   1. py -3.12 -m venv venv
    echo   2. .\venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
)
endlocal
