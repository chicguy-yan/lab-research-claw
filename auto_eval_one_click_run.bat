@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "BACKEND_URL=http://127.0.0.1:8002"
set "NO_PROXY=127.0.0.1,localhost"
set "PYTHONPATH=%BACKEND_DIR%\auto_eval\tests\runtime_stubs"
set "OPENAI_API_KEY="
set "OPENAI_BASE_URL="
set "OPENAI_MODEL="
set "TIMEOUT_SECONDS=900"
set "STATE_FILE=%BACKEND_DIR%\auto_eval\eval_runs\one_click_state.json"

if not exist "%BACKEND_DIR%\auto_eval\cli.py" (
  echo [ERROR] backend\auto_eval\cli.py not found
  exit /b 1
)

for /f "tokens=1,* delims==" %%A in ('python "%BACKEND_DIR%\auto_eval\one_click_state.py" init-or-resume "%STATE_FILE%"') do (
  set "%%A=%%B"
)

if /I "%MODE%"=="resume" (
  echo [STATE] Resuming existing one-click run stamp %RUN_STAMP%
) else (
  echo [STATE] Starting new one-click run stamp %RUN_STAMP%
)

echo [STATE] B=%RUN_B% (%STATUS_B%)
echo [STATE] C=%RUN_C% (%STATUS_C%)
echo [STATE] D=%RUN_D% (%STATUS_D%)
echo [STATE] E=%RUN_E% (%STATUS_E%)

set "B_SRC="
set "C_SRC="
set "D_SRC="
set "E_SRC="

for /d /r "%ROOT%" %%D in (B_*) do (
  if not defined B_SRC if exist "%%~fD\*obsidian*" set "B_SRC=%%~fD"
)
for /d /r "%ROOT%" %%D in (C_*) do (
  if not defined C_SRC if exist "%%~fD\*obsidian*" set "C_SRC=%%~fD"
)
for /d /r "%ROOT%" %%D in (D_*) do (
  if not defined D_SRC if exist "%%~fD\*obsidian*" set "D_SRC=%%~fD"
)
for /d /r "%ROOT%" %%D in (E_*) do (
  if not defined E_SRC if exist "%%~fD\*obsidian*" set "E_SRC=%%~fD"
)

if not defined B_SRC (
  echo [ERROR] scenario B dataset root not found
  exit /b 1
)
if not defined C_SRC (
  echo [ERROR] scenario C dataset root not found
  exit /b 1
)
if not defined D_SRC (
  echo [ERROR] scenario D dataset root not found
  exit /b 1
)
if not defined E_SRC (
  echo [ERROR] scenario E dataset root not found
  exit /b 1
)

echo [DATA] B = %B_SRC%
echo [DATA] C = %C_SRC%
echo [DATA] D = %D_SRC%
echo [DATA] E = %E_SRC%

echo ==================================================
echo [STEP] Starting backend on %BACKEND_URL%
echo ==================================================
powershell -NoProfile -Command "Start-Process -FilePath cmd.exe -ArgumentList '/c cd /d ""%ROOT%"" ^&^& call start_backend.bat 8002' -WindowStyle Minimized"

echo [STEP] Waiting for backend to become ready...
for /l %%I in (1,1,60) do (
  powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing '%BACKEND_URL%/' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
  if not errorlevel 1 goto backend_ready
  timeout /t 2 /nobreak >nul
)

echo [ERROR] Backend did not become ready within timeout.
exit /b 1

:backend_ready
echo [STEP] Backend is ready.

pushd "%BACKEND_DIR%"
if errorlevel 1 exit /b 1

call :run_scenario B "%B_SRC%" "%RUN_B%" "%STATUS_B%" "1/4"
if errorlevel 1 goto :fail
call :run_scenario C "%C_SRC%" "%RUN_C%" "%STATUS_C%" "2/4"
if errorlevel 1 goto :fail
call :run_scenario D "%D_SRC%" "%RUN_D%" "%STATUS_D%" "3/4"
if errorlevel 1 goto :fail
call :run_scenario E "%E_SRC%" "%RUN_E%" "%STATUS_E%" "4/4"
if errorlevel 1 goto :fail

echo.
echo [DONE] All four scenarios finished.
echo [STATE] State file: %STATE_FILE%
echo Reports are under backend\auto_eval\eval_runs\one_click_*
popd
exit /b 0

:run_scenario
set "SCENARIO=%~1"
set "SRC_ROOT=%~2"
set "RUN_ID=%~3"
set "SCENARIO_STATUS=%~4"
set "STEP_LABEL=%~5"

echo ==================================================
echo [%STEP_LABEL%] Running scenario %SCENARIO%
echo ==================================================

if /I "%SCENARIO_STATUS%"=="completed" (
  echo [SKIP] Scenario %SCENARIO% already completed in %RUN_ID%
  exit /b 0
)

python "%BACKEND_DIR%\auto_eval\one_click_state.py" update "%STATE_FILE%" "%SCENARIO%" running
python -m auto_eval.cli ^
  --backend-url %BACKEND_URL% ^
  --scenario %SCENARIO% ^
  --source-root "%SRC_ROOT%" ^
  --run-id %RUN_ID% ^
  --run-root auto_eval\eval_runs\%RUN_ID% ^
  --timeout-seconds %TIMEOUT_SECONDS% ^
  --resume
if errorlevel 1 (
  python "%BACKEND_DIR%\auto_eval\one_click_state.py" update "%STATE_FILE%" "%SCENARIO%" failed "auto_eval_cli_failed"
  exit /b 1
)
python "%BACKEND_DIR%\auto_eval\one_click_state.py" update "%STATE_FILE%" "%SCENARIO%" completed
exit /b 0

:fail
echo.
echo [FAILED] auto_eval_one_click_run.bat stopped because one scenario returned a non-zero exit code.
echo [STATE] Resume by rerunning the same bat. State file: %STATE_FILE%
popd
exit /b 1
