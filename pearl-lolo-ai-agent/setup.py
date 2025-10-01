#!/usr/bin/env python3
"""
Pearl Lolo AI Agent - Setup Script
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class PearlLoloInstaller:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.requirements_file = self.base_dir / "requirements.txt"
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            print("❌ Python 3.9 or higher is required")
            sys.exit(1)
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.requirements_file)
            ])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            "data/embeddings",
            "data/personalities", 
            "static/fonts",
            "static/images/icons",
            "logs"
        ]
        
        for dir_path in directories:
            full_path = self.base_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {dir_path}")
    
    def download_models(self):
        """Download required AI models"""
        print("🤖 Downloading AI models...")
        
        try:
            from models.download_models import download_core_models
            download_core_models()
            print("✅ Models downloaded successfully")
        except Exception as e:
            print(f"⚠️  Model download failed: {e}")
            print("You can download models later using the application")
    
    def setup_environment(self):
        """Setup environment variables"""
        # Add current directory to Python path
        if str(self.base_dir) not in sys.path:
            sys.path.insert(0, str(self.base_dir))
        
        # Create .env file if it doesn't exist
        env_file = self.base_dir / ".env"
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write("# Pearl Lolo AI Agent Environment Variables\n")
                f.write(f"PEARL_BASE_DIR={self.base_dir}\n")
    
    def run_checks(self):
        """Run system compatibility checks"""
        system = platform.system().lower()
        print(f"💻 Detected system: {system}")
        
        # Check available RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            if ram_gb < 4:
                print(f"⚠️  Low RAM detected: {ram_gb:.1f}GB (8GB+ recommended)")
            else:
                print(f"✅ RAM: {ram_gb:.1f}GB")
        except:
            print("⚠️  Could not check RAM")
    
    def install(self):
        """Run complete installation"""
        print("🚀 Starting Pearl Lolo AI Agent Installation...")
        print("=" * 50)
        
        self.check_python_version()
        self.setup_environment()
        self.create_directories()
        self.install_dependencies()
        self.run_checks()
        self.download_models()
        
        print("=" * 50)
        print("🎉 Installation completed successfully!")
        print("\nTo start the application:")
        print("  python main.py")
        print("  or")
        print("  ./run.sh (Linux/macOS)")
        print("  run.bat (Windows)")

if __name__ == "__main__":
    installer = PearlLoloInstaller()
    installer.install()