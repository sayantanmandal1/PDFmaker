@echo off
REM AI Document Generator API Startup Script for Windows

echo 🚀 AI Document Generator API Startup
echo ====================================

REM Check if we're in the backend directory
if not exist "main.py" (
    echo ❌ Error: Please run this script from the backend directory
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Error: Virtual environment not found. Please run 'python -m venv venv' first
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Using default environment variables.
)

REM Install/update dependencies
echo 📦 Checking dependencies...
pip install -r requirements.txt --quiet

REM Run database initialization if needed
echo 🗄️  Initializing database...
python init_db.py

REM Start the application
echo 🌟 Starting API server...
python start.py