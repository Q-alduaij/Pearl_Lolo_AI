#!/usr/bin/env python3
"""
Personality Engine - Manages AI personalities and response styles
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List

class PersonalityEngine:
    def __init__(self, config_manager):
        self.config = config_manager
        self.personalities = {}
        self.active_personality = "lolo"
        
        self.load_personalities()
    
    def load_personalities(self):
        """Load personality definitions from YAML files"""
        personalities_dir = Path("data/personalities")
        personalities_dir.mkdir(parents=True, exist_ok=True)
        
        # Load from YAML files
        for yaml_file in personalities_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    personality_data = yaml.safe_load(f)
                
                personality_name = personality_data.get('name', yaml_file.stem)
                self.personalities[personality_name] = personality_data
                print(f"✅ Loaded personality: {personality_name}")
                
            except Exception as e:
                print(f"❌ Failed to load personality {yaml_file}: {e}")
        
        # Ensure default personalities exist
        self._create_default_personalities()
    
    def _create_default_personalities(self):
        """Create default personality definitions"""
        default_personalities = {
            'lolo': {
                'name': 'Lolo',
                'description': 'Friendly, bilingual AI assistant',
                'language': 'both',
                'tone': 'friendly',
                'response_style': 'detailed',
                'traits': ['helpful', 'knowledgeable', 'empathetic', 'engaging'],
                'greeting': {
                    'english': 'Hello! I'm Lolo, your AI assistant. How can I help you today?',
                    'arabic': 'مرحباً! أنا لولو، مساعدك الذكي. كيف يمكنني مساعدتك اليوم؟'
                },
                'response_templates': {
                    'question': 'I'd be happy to help with that!',
                    'confusion': 'I'm not sure I understand. Could you please clarify?',
                    'thanks': 'You're welcome! Is there anything else I can help with?'
                }
            },
            'professional': {
                'name': 'Professional',
                'description': 'Formal and concise professional assistant',
                'language': 'english',
                'tone': 'formal',
                'response_style': 'concise',
                'traits': ['precise', 'efficient', 'factual', 'professional'],
                'greeting': {
                    'english': 'Good day. I am ready to assist you with your inquiries.',
                    'arabic': 'نهاركم سعيد. أنا جاهز لمساعدتكم في استفساراتكم.'
                },
                'response_templates': {
                    'question': 'I will address your inquiry.',
                    'confusion': 'Could you please provide more specific details?',
                    'thanks': 'You are welcome. Please let me know if you require further assistance.'
                }
            }
        }
        
        # Add missing default personalities
        for personality_name, personality_data in default_personalities.items():
            if personality_name not in self.personalities:
                self.personalities[personality_name] = personality_data
                self._save_personality_to_file(personality_name, personality_data)
    
    def _save_personality_to_file(self, personality_name: str, data: Dict[str, Any]):
        """Save personality to YAML file"""
        try:
            file_path = Path(f"data/personalities/{personality_name}.yaml")
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"❌ Failed to save personality {personality_name}: {e}")
    
    def get_personality(self, name: str = None) -> Dict[str, Any]:
        """Get personality configuration"""
        if name is None:
            name = self.active_personality
        
        return self.personalities.get(name, self.personalities['lolo'])
    
    def set_personality(self, name: str) -> bool:
        """Set active personality"""
        if name in self.personalities:
            self.active_personality = name
            self.config.set('personality.default', name)
            return True
        return False
    
    def get_available_personalities(self) -> List[str]:
        """Get list of available personality names"""
        return list(self.personalities.keys())
    
    def customize_personality(self, name: str, updates: Dict[str, Any]) -> bool:
        """Customize a personality"""
        if name not in self.personalities:
            return False
        
        try:
            # Update personality data
            self.personalities[name].update(updates)
            
            # Save to file
            self._save_personality_to_file(name, self.personalities[name])
            
            return True
        except Exception as e:
            print(f"❌ Failed to customize personality {name}: {e}")
            return False
    
    def create_personality(self, name: str, data: Dict[str, Any]) -> bool:
        """Create a new custom personality"""
        if name in self.personalities:
            return False
        
        try:
            # Ensure required fields
            required_fields = ['name', 'language', 'tone', 'response_style']
            for field in required_fields:
                if field not in data:
                    data[field] = 'default'
            
            self.personalities[name] = data
            self._save_personality_to_file(name, data)
            
            return True
        except Exception as e:
            print(f"❌ Failed to create personality {name}: {e}")
            return False
    
    def get_personality_greeting(self, personality_name: str = None) -> str:
        """Get greeting message for personality"""
        personality = self.get_personality(personality_name)
        greeting = personality.get('greeting', {})
        
        language = personality.get('language', 'both')
        
        if language == 'arabic':
            return greeting.get('arabic', 'مرحباً')
        elif language == 'english':
            return greeting.get('english', 'Hello')
        else:
            # Return both for mixed language
            arabic_greeting = greeting.get('arabic', 'مرحباً')
            english_greeting = greeting.get('english', 'Hello')
            return f"{english_greeting} / {arabic_greeting}"
    
    def apply_personality_style(self, response: str, personality_name: str = None) -> str:
        """Apply personality-specific styling to response"""
        personality = self.get_personality(personality_name)
        
        # Get personality traits
        traits = personality.get('traits', [])
        tone = personality.get('tone', 'neutral')
        response_style = personality.get('response_style', 'balanced')
        
        # Apply style modifications based on personality
        if 'empathetic' in traits:
            response = self._make_empathetic(response)
        
        if 'professional' in traits:
            response = self._make_professional(response)
        
        if 'concise' in response_style:
            response = self._make_concise(response)
        elif 'detailed' in response_style:
            response = self._make_detailed(response)
        
        return response
    
    def _make_empathetic(self, text: str) -> str:
        """Make text more empathetic"""
        # Simple empathetic enhancements
        empathetic_phrases = [
            "I understand how you feel about this.",
            "That's an important question.",
            "I appreciate you asking about this."
        ]
        
        # Don't modify if already empathetic
        if any(phrase in text for phrase in empathetic_phrases):
            return text
        
        # Add empathetic opening occasionally
        import random
        if random.random() < 0.3:  # 30% chance
            text = random.choice(empathetic_phrases) + " " + text
        
        return text
    
    def _make_professional(self, text: str) -> str:
        """Make text more professional"""
        # Remove casual language
        casual_words = {
            "hey": "hello",
            "yeah": "yes",
            "nah": "no",
            "gonna": "going to",
            "wanna": "want to"
        }
        
        for casual, formal in casual_words.items():
            text = text.replace(f" {casual} ", f" {formal} ")
        
        return text
    
    def _make_concise(self, text: str) -> str:
        """Make text more concise"""
        # Simple conciseness - limit to 3 sentences for demonstration
        sentences = text.split('. ')
        if len(sentences) > 3:
            text = '. '.join(sentences[:3]) + '.'
        
        return text
    
    def _make_detailed(self, text: str) -> str:
        """Make text more detailed"""
        # Ensure text has sufficient detail
        if len(text.split()) < 50:
            # Add encouraging note for more detail
            text += "\n\nPlease let me know if you would like more detailed information on any specific aspect."
        
        return text