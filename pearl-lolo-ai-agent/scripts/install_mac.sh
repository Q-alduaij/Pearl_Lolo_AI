#!/bin/bash

# Pearl Lolo AI Agent - macOS Installation Script

echo "🍎 Pearl Lolo AI Agent - macOS Installation"
echo "============================================"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "🐍 Installing Python 3.9..."
    brew install python@3.9
fi

# Verify Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION detected"

# Create and activate virtual environment
echo "🔧 Setting up virtual environment..."
python3 -m venv pearl-lolo-venv
source pearl-lolo-venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install Ollama for local AI
echo "🤖 Installing Ollama for local AI..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Download AI models
echo "📥 Downloading AI models..."
python -c "from models.download_models import download_core_models; download_core_models()"

# Create startup script
echo "🚀 Creating startup script..."
cat > start_pearl_lolo.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source pearl-lolo-venv/bin/activate
python main.py
EOF

chmod +x start_pearl_lolo.sh

# Create desktop shortcut (optional)
echo "🎯 Creating Application shortcut..."
cat > ~/Desktop/Start\ Pearl\ Lolo.command << 'EOF'
#!/bin/bash
cd "/Applications/Pearl Lolo AI Agent" 2>/dev/null || cd "$(dirname "$0")"
./start_pearl_loco.sh
EOF

chmod +x ~/Desktop/Start\ Pearl\ Lolo.command

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📋 Next Steps:"
echo "1. Start Ollama service:"
echo "   ollama serve"
echo ""
echo "2. Download a language model:"
echo "   ollama pull llama2"
echo ""
echo "3. Start Pearl Lolo AI:"
echo "   ./start_pearl_lolo.sh"
echo ""
echo "4. Or click 'Start Pearl Lolo' on your desktop"
echo ""
echo "🌐 The app will open at: http://localhost:8501"
echo ""