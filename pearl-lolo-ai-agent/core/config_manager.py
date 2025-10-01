#!/usr/bin/env python3
"""
Configuration Manager - FIXED VERSION
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.default_config = self._get_default_config()
        self.config = self._load_config()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/app.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get complete default configuration"""
        return {
            'app': {
                'name': 'Pearl Lolo AI Agent',
                'version': '1.0.0',
                'language': 'both',
                'debug': False
            },
            'ui': {
                'theme': 'glassmorphism',
                'primary_color': '#d2cdbd',
                'secondary_color': '#95b3f4',
                'font_primary': 'Inter, Arial, sans-serif',
                'font_code': 'Source Code Pro, monospace',
                'language': 'both'
            },
            'ai': {
                'default_model': 'local',
                'models': {
                    'local': {
                        'provider': 'ollama',
                        'model': 'llama2',
                        'base_url': 'http://localhost:11434',
                        'timeout': 30
                    },
                    'openai': {
                        'api_key': '',
                        'model': 'gpt-3.5-turbo',
                        'base_url': 'https://api.openai.com/v1'
                    },
                    'anthropic': {
                        'api_key': '',
                        'model': 'claude-3-sonnet-20240229',
                        'base_url': 'https://api.anthropic.com'
                    },
                    'google': {
                        'api_key': '',
                        'model': 'gemini-pro'
                    }
                }
            },
            'rag': {
                'enabled': True,
                'embedding_model': 'all-MiniLM-L6-v2',
                'vector_store': 'chromadb',
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'persist_directory': 'data/vector_store'
            },
            'search': {
                'enabled': False,
                'provider': 'google',
                'api_key': '',
                'search_engine_id': '',
                'num_results': 5
            },
            'personality': {
                'default': 'lolo',
                'profiles': {
                    'lolo': {
                        'name': 'Lolo',
                        'language': 'both',
                        'tone': 'friendly',
                        'response_style': 'detailed'
                    },
                    'professional': {
                        'name': 'Professional',
                        'language': 'english',
                        'tone': 'formal',
                        'response_style': 'concise'
                    },
                    'arabic': {
                        'name': 'Arabic Assistant',
                        'language': 'arabic',
                        'tone': 'respectful',
                        'response_style': 'detailed'
                    }
                }
            },
            'system': {
                'auto_update': True,
                'log_level': 'INFO',
                'max_memory': '8GB',
                'auto_save': True,
                'backup_interval': 3600
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with proper error handling"""
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f) or {}
                
                # Deep merge with defaults
                config = self._deep_merge(self.default_config, loaded_config)
                self.logger.info("Configuration loaded successfully")
            else:
                config = self.default_config.copy()
                self._save_config(config)
                self.logger.info("Created default configuration")
                
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Proper deep merge implementation"""
        result = base.copy()
        
        for key, value in update.items():
            if (key in result and isinstance(result[key], dict) 
                and isinstance(value, dict)):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration with error handling"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Safe configuration value retrieval"""
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
        except (KeyError, TypeError, AttributeError) as e:
            self.logger.debug(f"Config key not found: {key_path} - {e}")
            return default
    
    def set(self, key_path: str, value: Any, auto_save: bool = True) -> bool:
        """Safe configuration value setting"""
        try:
            keys = key_path.split('.')
            config_ref = self.config
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in config_ref or not isinstance(config_ref[key], dict):
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # Set value
            config_ref[keys[-1]] = value
            
            # Auto-save if enabled
            if auto_save and self.get('system.auto_save', True):
                return self._save_config(self.config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting config {key_path}: {e}")
            return False
    
    def update_batch(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values at once"""
        try:
            success = True
            for key_path, value in updates.items():
                if not self.set(key_path, value, auto_save=False):
                    success = False
            
            if success and self.get('system.auto_save', True):
                return self._save_config(self.config)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error in batch update: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return issues"""
        issues = {}
        
        # Check required API keys if services are enabled
        if self.get('search.enabled') and not self.get('search.api_key'):
            issues['search'] = 'Search enabled but no API key provided'
        
        # Check model configurations
        default_model = self.get('ai.default_model')
        if default_model not in ['local', 'openai', 'anthropic', 'google']:
            issues['ai'] = f'Invalid default model: {default_model}'
        
        # Check file paths
        rag_path = Path(self.get('rag.persist_directory', 'data/vector_store'))
        if not rag_path.parent.exists():
            issues['paths'] = f'RAG directory parent does not exist: {rag_path.parent}'
        
        return issues
    
    def reset_to_defaults(self) -> bool:
        """Reset to default configuration"""
        try:
            self.config = self.default_config.copy()
            return self._save_config(self.config)
        except Exception as e:
            self.logger.error(f"Error resetting config: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get complete configuration"""
        return self.config.copy()