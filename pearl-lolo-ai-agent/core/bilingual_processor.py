#!/usr/bin/env python3
"""
Bilingual Processor - Handles Arabic/English text processing
"""

import re
import arabic_reshaper
from bidi.algorithm import get_display
from typing import Tuple, List

class BilingualProcessor:
    def __init__(self):
        self.arabic_chars = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        self.english_chars = re.compile(r'[a-zA-Z]')
    
    def detect_language(self, text: str) -> str:
        """Detect if text is Arabic, English, or mixed"""
        if not text:
            return 'unknown'
        
        arabic_count = len(self.arabic_chars.findall(text))
        english_count = len(self.english_chars.findall(text))
        total_letters = arabic_count + english_count
        
        if total_letters == 0:
            return 'unknown'
        
        arabic_ratio = arabic_count / total_letters
        english_ratio = english_count / total_letters
        
        if arabic_ratio > 0.7:
            return 'arabic'
        elif english_ratio > 0.7:
            return 'english'
        else:
            return 'mixed'
    
    def reshape_arabic(self, text: str) -> str:
        """Reshape Arabic text for proper display"""
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except Exception as e:
            print(f"❌ Arabic reshaping error: {e}")
            return text
    
    def process_text(self, text: str) -> str:
        """Process text for proper bilingual display"""
        if self.detect_language(text) == 'arabic':
            return self.reshape_arabic(text)
        return text
    
    def split_mixed_text(self, text: str) -> List[Tuple[str, str]]:
        """Split mixed text into language segments"""
        segments = []
        current_segment = ""
        current_lang = "unknown"
        
        for char in text:
            char_lang = self.detect_language(char)
            
            if char_lang != current_lang and current_segment:
                segments.append((current_segment, current_lang))
                current_segment = ""
            
            current_segment += char
            current_lang = char_lang
        
        if current_segment:
            segments.append((current_segment, current_lang))
        
        return segments
    
    def is_rtl(self, text: str) -> bool:
        """Check if text should be displayed right-to-left"""
        return self.detect_language(text) in ['arabic', 'mixed']
    
    def get_text_direction(self, text: str) -> str:
        """Get CSS text direction for the text"""
        return 'rtl' if self.is_rtl(text) else 'ltr'
    
    def translate_interface(self, key: str, language: str = 'both') -> str:
        """Translate interface elements"""
        translations = {
            'welcome': {
                'english': 'Welcome to Pearl Lolo AI Assistant',
                'arabic': 'مرحباً بكم في مساعد لولو الذكي'
            },
            'ask_anything': {
                'english': 'Ask me anything...',
                'arabic': 'اسألني أي شيء...'
            },
            'thinking': {
                'english': 'Thinking...',
                'arabic': 'جاري التفكير...'
            },
            'settings': {
                'english': 'Settings',
                'arabic': 'الإعدادات'
            },
            'language': {
                'english': 'Language',
                'arabic': 'اللغة'
            }
        }
        
        if key not in translations:
            return key
        
        if language == 'arabic':
            return translations[key]['arabic']
        elif language == 'english':
            return translations[key]['english']
        else:
            # Return both languages for mixed interface
            return f"{translations[key]['english']} / {translations[key]['arabic']}"