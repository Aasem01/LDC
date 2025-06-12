@echo off
echo Starting RAG Chatbot Application...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Upgrade pip
@REM python -m pip install --upgrade pip

:: Install/update requirements
@REM echo Installing/updating requirements...
@REM pip install -r requirements.txt

:: Create logs directory if it doesn't exist
if not exist logs mkdir logs

:: Run the application
echo Starting the application...
python main.py

:: Deactivate virtual environment on exit
call venv\Scripts\deactivate

pause 