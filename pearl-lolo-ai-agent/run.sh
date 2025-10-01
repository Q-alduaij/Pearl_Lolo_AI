#!/bin/bash

# Pearl Lolo AI Agent - Startup Script for macOS/Linux

echo "🚀 Starting Pearl Lolo AI Agent..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if not already installed
if [ ! -f "installed.flag" ]; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create installed flag
    touch installed.flag
    echo "✅ Dependencies installed"
fi

# Check if models are downloaded
if [ ! -f "data/embeddings/download_complete.flag" ]; then
    echo "🤖 Downloading AI models (this may take a while)..."
    python -c "from models.download_models import download_core_models; download_core_models()"
    touch data/embeddings/download_complete.flag
fi

# Start the application
echo "🎯 Starting application..."
echo "💡 The application will open in your browser at http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"

python main.py