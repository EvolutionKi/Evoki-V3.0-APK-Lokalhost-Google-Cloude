@echo off
echo ==========================================
echo   EVOKI V3.0 CLEANUP SCRIPT (FORCE)
echo   [LEGACY REMOVAL TOOL - app/temple refs are intentional]
echo ==========================================
echo.
echo Dieses Script beendet ALLE Python Prozesse und loescht app/temple.
echo.
echo ACHTUNG: Der neue Watcher wird auch beendet. Starten Sie ihn danach neu!
echo.
pause
echo.
echo Beende Python Prozesse...
taskkill /F /IM python.exe
echo.
echo Warte kurz...
timeout /t 2 /nobreak
echo.
echo Loesche app/temple...
rmdir /S /Q "app\temple"
echo.
if exist "app\temple" (
    echo [ERROR] Ordner konnte immer noch nicht geloescht werden.
) else (
    echo [OK] Bereinigung erfolgreich!
    echo Bitte starten Sie jetzt den Watcher neu:
    echo python "tooling\scripts\daemons\pending_status_watcher.py"
)
pause
