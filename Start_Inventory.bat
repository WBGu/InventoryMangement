@echo off
TITLE Inventory System Launcher

:: Navigate to the folder where this .bat file is located
cd /d "%~dp0"

echo Starting Inventory System POS...

:: Launch the Python script with command prompt
:: python main.py

:: Launch the Python script without command prompt
pythonw main.py

:: Check if the app crashed
if %errorlevel% neq 0 (
    echo.
    echo =======================================================
    echo ERROR: The application crashed or failed to start.
    echo Make sure you have installed the required libraries!
    echo Run this command in your terminal: pip install tksheet
    echo =======================================================
    pause
)