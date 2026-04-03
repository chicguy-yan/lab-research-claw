@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT_DIR=%~dp0"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=%BACKEND_PORT%"
if "%PORT%"=="" set "PORT=8002"

set "BACKEND_DIR=%ROOT_DIR%backend"
set "PYTHON_EXE=%BACKEND_DIR%\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

echo [backend] Preparing to start backend on port %PORT%

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    if not "%%P"=="0" (
        echo [backend] Killing process %%P on port %PORT%
        taskkill /F /PID %%P >nul 2>&1
    )
)

pushd "%BACKEND_DIR%" >nul 2>&1
if errorlevel 1 (
    echo [backend] Cannot find backend directory: "%BACKEND_DIR%"
    exit /b 1
)

if not exist app.py (
    echo [backend] app.py not found in "%CD%"
    popd >nul
    exit /b 1
)

echo [backend] Starting backend from "%CD%"
echo [backend] Python: %PYTHON_EXE%
call "%PYTHON_EXE%" -m uvicorn app:app --host 0.0.0.0 --port %PORT% --reload
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
