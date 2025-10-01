@echo off
title Pearl Lolo AI Agent - Windows

echo 🚀 Starting Pearl Lolo AI Agent...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo ✅ Python %PYTHON_VERSION% detected

:: Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies if not already installed
if not exist "installed.flag" (
    echo 📥 Installing dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
    
    :: Create installed flag
    type nul > installed.flag
    echo ✅ Dependencies installed
)

:: Check if models are downloaded
if not exist "data\embeddings\download_complete.flag" (
    echo 🤖 Downloading AI models (this may take a while)...
    python -c "from models.download_models import download_core_models; download_core_models()"
    type nul > data\embeddings\download_complete.flag
)

:: Start the application
echo 🎯 Starting application...
echo 💡 The application will open in your browser at http://localhost:8501
echo 🛑 Press Ctrl+C to stop the application

python main.py

pause