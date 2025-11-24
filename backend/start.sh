#!/bin/bash

# AI Document Generator API Startup Script

set -e  # Exit on any error

echo "🚀 AI Document Generator API Startup"
echo "===================================="

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run 'python -m venv venv' first"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/macOS
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Using default environment variables."
fi

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install -r requirements.txt --quiet

# Run database initialization if needed
echo "🗄️  Initializing database..."
python init_db.py

# Start the application
echo "🌟 Starting API server..."
python start.py