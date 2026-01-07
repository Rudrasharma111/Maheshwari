@echo off
:: 1. Move to the current folder
cd /d "%~dp0"

:: 2. Open the Dashboard in Chrome automatically
start "" "http://127.0.0.1:5000"

:: 3. Run the Python Server
echo Starting Maheshwari Fertilizer Bot...
python app.py

:: 4. Keep window open if there is an error
pause