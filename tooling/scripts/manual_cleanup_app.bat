@echo off
echo ==========================================
echo   EVOKI V3.0 CLEANUP SCRIPT
echo ==========================================
echo.
echo Dieses Script loescht den alten 'app/temple' Ordner.
echo.
echo ACHTUNG: Bitte beenden Sie zuerst alle laufenden Watcher!
echo (Ctrl+C im Terminal wo pending_status_watcher.py laeuft)
echo.
pause
echo.
echo Loesche app/temple...
rmdir /S /Q "app\temple"

if exist "app\temple" (
    echo [ERROR] Konnte Ordner nicht loeschen.
    echo Ein Prozess (Watcher/Editor) greift noch darauf zu.
    echo Bitte Prozess beenden und erneut versuchen.
    exit /b 1
) else (
    echo [OK] app/temple erfolgreich entfernt.
    echo Struktur ist nun sauber: Logic liegt in tooling/scripts/automation.
)
pause
