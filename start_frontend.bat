@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT_DIR=%~dp0"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=%FRONTEND_PORT%"
if "%PORT%"=="" set "PORT=5173"

echo [frontend] Preparing to start Vite on port %PORT%

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    if not "%%P"=="0" (
        echo [frontend] Killing process %%P on port %PORT%
        taskkill /F /PID %%P >nul 2>&1
    )
)

pushd "%ROOT_DIR%frontend" >nul 2>&1
if errorlevel 1 (
    echo [frontend] Cannot find frontend directory: "%ROOT_DIR%frontend"
    exit /b 1
)

if not exist package.json (
    echo [frontend] package.json not found in "%CD%"
    popd >nul
    exit /b 1
)

echo [frontend] Starting dev server from "%CD%"
call npm.cmd run dev -- --host 0.0.0.0 --port %PORT%
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
