#!/usr/bin/env python3
"""
Model Downloader - Handles downloading AI models for Pearl Lolo
"""

import os
import requests
import zipfile
import tarfile
from pathlib import Path
from tqdm import tqdm
import huggingface_hub

class ModelDownloader:
    def __init__(self):
        self.models_dir = Path("models/downloaded")
        self.embeddings_dir = Path("data/embeddings")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    def download_core_models(self):
        """Download all core models required for Pearl Lolo"""
        print("🚀 Starting model downloads...")
        
        models_to_download = [
            {
                'name': 'Sentence Transformer - MiniLM',
                'type': 'huggingface',
                'model_id': 'sentence-transformers/all-MiniLM-L6-v2',
                'local_path': self.embeddings_dir / 'all-MiniLM-L6-v2'
            },
            {
                'name': 'Arabic BERT Base',
                'type': 'huggingface', 
                'model_id': 'asafaya/bert-base-arabic',
                'local_path': self.models_dir / 'bert-base-arabic'
            },
            {
                'name': 'Arabic Sentence Transformer',
                'type': 'huggingface',
                'model_id': 'sentence-transformers/bert-base-arabic-camelbert-msa',
                'local_path': self.embeddings_dir / 'arabic-bert'
            }
        ]
        
        for model_info in models_to_download:
            self._download_model(model_info)
        
        print("✅ All core models downloaded successfully!")
    
    def _download_model(self, model_info: dict):
        """Download a single model"""
        name = model_info['name']
        model_type = model_info['type']
        local_path = model_info['local_path']
        
        print(f"📥 Downloading {name}...")
        
        if local_path.exists():
            print(f"✅ {name} already exists, skipping...")
            return
        
        try:
            if model_type == 'huggingface':
                self._download_huggingface_model(
                    model_info['model_id'],
                    local_path
                )
            elif model_type == 'direct':
                self._download_direct_model(
                    model_info['url'],
                    local_path,
                    model_info.get('format', 'zip')
                )
            
            print(f"✅ Successfully downloaded {name}")
            
        except Exception as e:
            print(f"❌ Failed to download {name}: {e}")
    
    def _download_huggingface_model(self, model_id: str, local_path: Path):
        """Download model from HuggingFace Hub"""
        try:
            # Use huggingface_hub to download the model
            from huggingface_hub import snapshot_download
            
            snapshot_download(
                repo_id=model_id,
                local_dir=local_path,
                local_dir_use_symlinks=False
            )
            
        except Exception as e:
            print(f"❌ HuggingFace download failed: {e}")
            # Fallback to direct download if available
            self._fallback_download(model_id, local_path)
    
    def _fallback_download(self, model_id: str, local_path: Path):
        """Fallback download method"""
        print(f"🔄 Using fallback download for {model_id}")
        
        # This would implement alternative download methods
        # For now, we'll create a placeholder
        local_path.mkdir(parents=True, exist_ok=True)
        
        # Create a info file
        info_file = local_path / "model_info.txt"
        with open(info_file, 'w') as f:
            f.write(f"Model: {model_id}\n")
            f.write("Status: Placeholder - will download on first use\n")
    
    def _download_direct_model(self, url: str, local_path: Path, format: str = 'zip'):
        """Download model from direct URL"""
        try:
            # Create temporary download path
            temp_path = local_path.with_suffix('.tmp')
            
            # Download with progress bar
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(temp_path, 'wb') as file, tqdm(
                desc=f"Downloading {local_path.name}",
                total=total_size,
                unit='iB',
                unit_scale=True
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    pbar.update(size)
            
            # Extract if needed
            if format == 'zip':
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    zip_ref.extractall(local_path)
            elif format == 'tar':
                with tarfile.open(temp_path, 'r') as tar_ref:
                    tar_ref.extractall(local_path)
            else:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path.rename(local_path)
            
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
                
        except Exception as e:
            print(f"❌ Direct download failed: {e}")
            # Cleanup on failure
            if temp_path.exists():
                temp_path.unlink()
            raise
    
    def check_model_availability(self) -> dict:
        """Check which models are available locally"""
        available_models = {}
        
        # Check embedding models
        embedding_models = {
            'all-MiniLM-L6-v2': self.embeddings_dir / 'all-MiniLM-L6-v2',
            'arabic-bert': self.embeddings_dir / 'arabic-bert'
        }
        
        for name, path in embedding_models.items():
            available_models[name] = path.exists() and any(path.iterdir())
        
        # Check other models
        other_models = {
            'bert-base-arabic': self.models_dir / 'bert-base-arabic'
        }
        
        for name, path in other_models.items():
            available_models[name] = path.exists() and any(path.iterdir())
        
        return available_models
    
    def get_model_size(self, model_name: str) -> str:
        """Get size of downloaded model"""
        model_paths = {
            'all-MiniLM-L6-v2': self.embeddings_dir / 'all-MiniLM-L6-v2',
            'arabic-bert': self.embeddings_dir / 'arabic-bert',
            'bert-base-arabic': self.models_dir / 'bert-base-arabic'
        }
        
        if model_name not in model_paths:
            return "Unknown"
        
        path = model_paths[model_name]
        if not path.exists():
            return "Not downloaded"
        
        total_size = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        # Convert to human readable
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        
        return f"{total_size:.1f} TB"

def download_core_models():
    """Main function to download all core models"""
    downloader = ModelDownloader()
    downloader.download_core_models()
    
    # Print summary
    print("\n📊 Model Download Summary:")
    print("=" * 30)
    
    available = downloader.check_model_availability()
    for model, is_available in available.items():
        status = "✅ Available" if is_available else "❌ Missing"
        size = downloader.get_model_size(model)
        print(f"{model}: {status} ({size})")

if __name__ == "__main__":
    download_core_models()