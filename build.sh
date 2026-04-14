#!/usr/bin/env bash
# Build a single-file binary using PyInstaller on macOS/Linux.
# (On Windows use build.bat instead.)
set -e

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

python -m PyInstaller \
    --noconsole \
    --onefile \
    --name "NoteMariLaFizica" \
    --collect-submodules app \
    main.py

echo "Built: dist/NoteMariLaFizica"
