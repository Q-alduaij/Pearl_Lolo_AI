#!/usr/bin/env python3
"""
Environment Setup - Configures the runtime environment for Pearl Lolo
"""

import os
import sys
import platform
from pathlib import Path

class EnvironmentSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.home_dir = Path.home()
        self.project_dir = Path(__file__).parent.parent
        
    def setup_environment(self):
        """Setup the complete runtime environment"""
        print("🔧 Setting up Pearl Lolo environment...")
        
        self.create_directories()
        self.setup_python_path()
        self.setup_environment_variables()
        self.check_system_requirements()
        self.create_config_files()
        
        print("✅ Environment setup complete!")
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            "data/embeddings",
            "data/personalities",
            "data/uploads", 
            "models/downloaded",
            "logs",
            "static/fonts",
            "static/images/icons",
            "temp"
        ]
        
        for dir_path in directories:
            full_path = self.project_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {dir_path}")
    
    def setup_python_path(self):
        """Add project directories to Python path"""
        project_root = str(self.project_dir)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Add core and ui directories
        core_dir = str(self.project_dir / "core")
        ui_dir = str(self.project_dir / "ui")
        models_dir = str(self.project_dir / "models")
        
        for dir_path in [core_dir, ui_dir, models_dir]:
            if dir_path not in sys.path:
                sys.path.insert(0, dir_path)
    
    def setup_environment_variables(self):
        """Setup environment variables"""
        env_vars = {
            'PEARL_LOLO_HOME': str(self.project_dir),
            'PYTHONPATH': f"{self.project_dir}/core:{self.project_dir}/ui:{self.project_dir}/models",
            'MODELS_DIR': str(self.project_dir / "models/downloaded"),
            'DATA_DIR': str(self.project_dir / "data"),
            'LOG_LEVEL': 'INFO'
        }
        
        # Create .env file
        env_file = self.project_dir / ".env"
        with open(env_file, 'w') as f:
            f.write("# Pearl Lolo AI Agent Environment Variables\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        # Set environment variables for current session
        for key, value in env_vars.items():
            os.environ[key] = value
        
        print("🔧 Environment variables configured")
    
    def check_system_requirements(self):
        """Check system requirements"""
        print("🔍 Checking system requirements...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
            print("❌ Python 3.9 or higher is required")
            sys.exit(1)
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check available RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            if ram_gb < 4:
                print(f"⚠️  Low RAM: {ram_gb:.1f}GB (8GB+ recommended)")
            else:
                print(f"✅ RAM: {ram_gb:.1f}GB")
        except ImportError:
            print("⚠️  Could not check RAM (psutil not installed)")
        
        # Check disk space
        try:
            disk_usage = psutil.disk_usage(str(self.project_dir))
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 5:
                print(f"⚠️  Low disk space: {free_gb:.1f}GB free")
            else:
                print(f"✅ Disk space: {free_gb:.1f}GB free")
        except:
            print("⚠️  Could not check disk space")
        
        # Check for CUDA (optional)
        try:
            import torch
            if torch.cuda.is_available():
                print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            else:
                print("ℹ️  CUDA not available - using CPU")
        except ImportError:
            print("ℹ️  PyTorch not installed yet")
    
    def create_config_files(self):
        """Create default configuration files"""
        # Check if config already exists
        config_file = self.project_dir / "config.yaml"
        if not config_file.exists():
            print("📝 Creating default configuration...")
            
            # Copy from default template
            default_config = self.project_dir / "config_default.yaml"
            if default_config.exists():
                import shutil
                shutil.copy2(default_config, config_file)
            else:
                # Create basic config
                self.create_default_config(config_file)
    
    def create_default_config(self, config_path: Path):
        """Create default configuration file"""
        import yaml
        
        default_config = {
            'app': {
                'name': 'Pearl Lolo AI Agent',
                'version': '1.0.0',
                'language': 'both'
            },
            'ui': {
                'theme': 'glassmorphism',
                'primary_color': '#d2cdbd',
                'secondary_color': '#95b3f4',
                'font_primary': 'Inter',
                'font_code': 'Source Code Pro'
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        
        requirements_file = self.project_dir / "requirements.txt"
        if requirements_file.exists():
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
            print("✅ Dependencies installed")
        else:
            print("❌ requirements.txt not found")
    
    def setup_complete(self):
        """Run complete setup process"""
        print("🚀 Starting complete Pearl Lolo setup...")
        print("=" * 50)
        
        self.setup_environment()
        self.install_dependencies()
        
        print("=" * 50)
        print("🎉 Setup complete! You can now run:")
        print("   python main.py")
        print("   or")
        print("   ./run.sh")

if __name__ == "__main__":
    setup = EnvironmentSetup()
    setup.setup_complete()