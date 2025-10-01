#!/usr/bin/env python3
"""
Model Manager - Manages AI model loading and switching for Pearl Lolo
"""

import os
import torch
from typing import Dict, Any, List, Optional
from pathlib import Path

class ModelManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.loaded_models = {}
        self.current_model = None
        
    def load_model(self, model_type: str, model_name: str, **kwargs) -> bool:
        """Load a specific model"""
        try:
            if model_type == "embedding":
                return self._load_embedding_model(model_name, **kwargs)
            elif model_type == "language":
                return self._load_language_model(model_name, **kwargs)
            elif model_type == "classification":
                return self._load_classification_model(model_name, **kwargs)
            else:
                print(f"❌ Unknown model type: {model_type}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to load model {model_name}: {e}")
            return False
    
    def _load_embedding_model(self, model_name: str, **kwargs) -> bool:
        """Load an embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            cache_dir = kwargs.get('cache_dir', 'models/downloaded')
            device = kwargs.get('device', 'cpu')
            
            model = SentenceTransformer(
                model_name,
                cache_folder=cache_dir,
                device=device
            )
            
            self.loaded_models[f"embedding_{model_name}"] = model
            print(f"✅ Loaded embedding model: {model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load embedding model {model_name}: {e}")
            return False
    
    def _load_language_model(self, model_name: str, **kwargs) -> bool:
        """Load a language model"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            cache_dir = kwargs.get('cache_dir', 'models/downloaded')
            device = kwargs.get('device', 'cpu')
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
                device_map="auto" if device == 'cuda' else None
            )
            
            self.loaded_models[f"language_{model_name}"] = {
                'tokenizer': tokenizer,
                'model': model
            }
            
            print(f"✅ Loaded language model: {model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load language model {model_name}: {e}")
            return False
    
    def _load_classification_model(self, model_name: str, **kwargs) -> bool:
        """Load a classification model"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            cache_dir = kwargs.get('cache_dir', 'models/downloaded')
            device = kwargs.get('device', 'cpu')
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir
            )
            
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                num_labels=kwargs.get('num_labels', 2)
            )
            
            self.loaded_models[f"classification_{model_name}"] = {
                'tokenizer': tokenizer,
                'model': model
            }
            
            print(f"✅ Loaded classification model: {model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load classification model {model_name}: {e}")
            return False
    
    def get_model(self, model_type: str, model_name: str):
        """Get a loaded model"""
        key = f"{model_type}_{model_name}"
        return self.loaded_models.get(key)
    
    def unload_model(self, model_type: str, model_name: str) -> bool:
        """Unload a model to free memory"""
        key = f"{model_type}_{model_name}"
        
        if key in self.loaded_models:
            del self.loaded_models[key]
            
            # Force garbage collection
            import gc
            gc.collect()
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print(f"✅ Unloaded model: {model_name}")
            return True
        
        return False
    
    def get_loaded_models(self) -> List[str]:
        """Get list of loaded models"""
        return list(self.loaded_models.keys())
    
    def get_model_memory_usage(self) -> Dict[str, str]:
        """Get memory usage of loaded models"""
        memory_usage = {}
        
        for model_name, model_obj in self.loaded_models.items():
            if isinstance(model_obj, dict) and 'model' in model_obj:
                # For transformer models
                model = model_obj['model']
                param_count = sum(p.numel() for p in model.parameters())
                memory_usage[model_name] = f"{param_count:,} parameters"
            else:
                # For other models
                memory_usage[model_name] = "Size unknown"
        
        return memory_usage
    
    def optimize_for_device(self, device: str = 'cpu') -> bool:
        """Optimize models for specific device"""
        try:
            for model_name, model_obj in self.loaded_models.items():
                if isinstance(model_obj, dict) and 'model' in model_obj:
                    model_obj['model'] = model_obj['model'].to(device)
                elif hasattr(model_obj, 'to'):
                    model_obj = model_obj.to(device)
            
            print(f"✅ Optimized models for device: {device}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to optimize models: {e}")
            return False
    
    def switch_active_model(self, model_type: str, model_name: str) -> bool:
        """Switch active model for inference"""
        key = f"{model_type}_{model_name}"
        
        if key in self.loaded_models:
            self.current_model = key
            self.config.set('ai.active_model', key)
            print(f"✅ Switched to model: {model_name}")
            return True
        else:
            # Try to load the model
            if self.load_model(model_type, model_name):
                self.current_model = key
                self.config.set('ai.active_model', key)
                return True
        
        return False