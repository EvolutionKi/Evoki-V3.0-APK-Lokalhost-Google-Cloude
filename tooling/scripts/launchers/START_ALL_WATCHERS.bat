@echo off
REM ═══════════════════════════════════════════════════════════════════
REM              EVOKI V3.0 - COMPLETE WATCHER SUITE
REM ═══════════════════════════════════════════════════════════════════
REM Startet BEIDE Watcher für vollständiges Compliance-Monitoring:
REM   1. pending_status_watcher.py - Status Window Logging
REM   2. context_watcher.py - User-Prompt Erfassung aus VSCode DB
REM ═══════════════════════════════════════════════════════════════════

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║           EVOKI V3.0 - COMPLETE WATCHER SUITE                     ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

cd /d "c:\Evoki V3.0 APK-Lokalhost-Google Cloude"

echo [1/2] Starting Pending Status Watcher...
start "Pending Status Watcher" cmd /k "python app\temple\automation\pending_status_watcher.py"

echo [2/2] Starting Context Watcher (User-Prompt Erfassung)...
start "Context Watcher" cmd /k "python tooling\scripts\daemons\context_watcher.py --monitor"

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   ✅ BEIDE WATCHER GESTARTET!
echo.
echo   📊 Pending Status Watcher: Loggt alle Status Windows
echo   📝 Context Watcher: Erfasst alle User-Prompts aus VSCode DB
echo.
echo   💡 Compliance Check: python tooling\scripts\cli\prompt_compliance_checker.py
echo ═══════════════════════════════════════════════════════════════════
echo.

pause
