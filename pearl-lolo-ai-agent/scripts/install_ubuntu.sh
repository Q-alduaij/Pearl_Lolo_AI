#!/bin/bash

# Pearl Lolo AI Agent - Ubuntu Installation Script

echo "🐧 Pearl Lolo AI Agent - Ubuntu Installation"
echo "============================================"

# Update package list
echo "🔄 Updating package list..."
sudo apt update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y python3.9 python3.9-venv python3-pip git curl

# Verify Python installation
echo "✅ Python 3.9 installed"

# Create project directory
echo "📁 Setting up project directory..."
mkdir -p ~/pearl-lolo-ai
cd ~/pearl-lolo-ai

# Create and activate virtual environment
echo "🔧 Setting up virtual environment..."
python3.9 -m venv pearl-lolo-venv
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

# Add current user to Ollama group
echo "👥 Adding user to Ollama group..."
sudo usermod -a -G ollama $USER

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

# Create desktop entry
echo "🎯 Creating desktop entry..."
cat > ~/.local/share/applications/pearl-lolo-ai.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pearl Lolo AI Agent
Comment=AI Assistant with Arabic/English Support
Exec=$HOME/pearl-lolo-ai/start_pearl_lolo.sh
Icon=utilities-terminal
Terminal=false
Categories=Office;Education;Development;
EOF

# Make desktop entry executable
chmod +x ~/.local/share/applications/pearl-lolo-ai.desktop

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
echo "4. Or find 'Pearl Lolo AI Agent' in your applications menu"
echo ""
echo "🌐 The app will open at: http://localhost:8501"
echo ""
echo "🔧 Note: You may need to logout and login again for group changes to take effect"
echo ""