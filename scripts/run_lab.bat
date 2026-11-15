@echo off
rem Lab-PC runner (Windows). Usage, from the repository root with the venv activated:
rem     scripts\run_lab.bat smoke     environment check + pipeline self-test on synthetic data
rem     scripts\run_lab.bat full      the registered real-data run (rule D24b), scale_up config
rem Progress:  powershell Get-Content logs\real_run.log -Wait
setlocal
set PYTHONUTF8=1
set CUBLAS_WORKSPACE_CONFIG=:4096:8
if not exist logs mkdir logs
if "%1"=="" goto usage

python scripts\check_env.py --config configs\scale_up.yaml > logs\check_env.log 2>&1
type logs\check_env.log
findstr /C:"CHECK PASSED" logs\check_env.log >nul || goto fail

if "%1"=="smoke" (
  python scripts\run_real_all.py --standin --config configs\smoke.yaml > logs\smoke.log 2>&1 || goto fail
  echo SMOKE TEST PASSED. Outputs in results\standin are meaningless and are not committed.
  goto end
)
if "%1"=="full" (
  if not exist data\interim\miss_logs.parquet (
    echo data\interim\miss_logs.parquet is missing: run the data and audit steps first.
    goto fail
  )
  python scripts\run_real_all.py --config configs\scale_up.yaml > logs\real_run.log 2>&1 || goto fail
  if not exist results\real\run_logs mkdir results\real\run_logs
  copy /Y logs\check_env.log results\real\run_logs\ >nul
  copy /Y logs\real_run.log results\real\run_logs\ >nul
  echo FULL RUN FINISHED. Verdict: results\real\evaluation.json
  goto end
)
:usage
echo Usage: scripts\run_lab.bat smoke ^| full
goto end
:fail
echo FAILED. See the newest file in logs\ and send it back.
exit /b 1
:end
endlocal
