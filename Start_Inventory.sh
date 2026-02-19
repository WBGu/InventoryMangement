#!/bin/bash

# Navigate to the folder where this script is located.
# This ensures it finds 'main.py' even if running from desktop shortcut.
cd "$(dirname "$0")" || exit

echo "Starting Inventory System..."

# Check which Python command is available on your system
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python is not installed or not in your system PATH."
    echo "Please install Python to run this application."
    read -p "Press Enter to exit..."
    exit 1
fi

# Launch the Python application
$PYTHON_CMD main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Crashed. Make sure you have installed the required libraries:"
    echo "Run: pip install tksheet"
    read -p "Press Enter to exit..."
fi