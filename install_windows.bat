@echo off
echo ==========================================
echo      OdinKey Installation (Windows)
echo ==========================================
echo.

:: Prüfen, ob Python installiert ist
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python wurde nicht gefunden!
    echo Bitte installieren Sie Python von python.org und aktivieren Sie "Add to PATH".
    pause
    exit /b
)

echo [INFO] Python gefunden. Installiere Abhaengigkeiten...
echo.

:: Wir nutzen python -m pip, um Fehler zu vermeiden
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [FEHLER] Es gab ein Problem bei der Installation.
    pause
    exit /b
)

echo.
echo [ERFOLG] Alle Pakete wurden installiert!
echo.
echo Sie koennen OdinKey jetzt starten:
echo.
echo A) CLI (Kommandozeile):
echo    python cli_main.py
echo.
echo B) GUI (Grafische Oberflaeche - Empfohlen):
echo    python src/gui/main_window.py
echo.
echo.
pause