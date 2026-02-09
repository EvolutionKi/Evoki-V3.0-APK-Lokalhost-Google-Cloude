@echo off
REM Import History with Python 3.12 (GPU Support)
echo ========================================
echo EVOKI V3.0 - History Import (GPU)
echo Python 3.12 + CUDA
echo ========================================
echo.

cd /d "%~dp0.."
py -3.12 utils\import_history_logs.py %*
