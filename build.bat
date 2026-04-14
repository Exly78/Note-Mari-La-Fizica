@echo off
REM Build a single-file Windows .exe using PyInstaller.
REM Requirements: Python 3.10+ and `pip install -r requirements.txt pyinstaller`

setlocal

where python >nul 2>&1
if errorlevel 1 (
    echo [error] Python is not on PATH. Install Python 3.10+ and try again.
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

REM --noconsole hides the black cmd window, --onefile makes a single exe,
REM --name sets the binary name, --collect-all Pillow ensures PIL ships.
python -m PyInstaller ^
    --noconsole ^
    --onefile ^
    --name "NoteMariLaFizica" ^
    --collect-submodules app ^
    main.py

echo.
echo Built: dist\NoteMariLaFizica.exe
endlocal
