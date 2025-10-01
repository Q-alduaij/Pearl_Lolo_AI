#!/usr/bin/env python3
"""
Arabic Support - RTL language support for Pearl Lolo UI
"""

import streamlit as st
import arabic_reshaper
from bidi.algorithm import get_display
from typing import Dict, Any

class ArabicSupport:
    def __init__(self):
        self.rtl_styles = {
            'container': {
                'direction': 'rtl',
                'text-align': 'right',
                'font-family': "'Segoe UI', 'Tahoma', 'Arial', sans-serif"
            },
            'input': {
                'text-align': 'right',
                'direction': 'rtl'
            },
            'textarea': {
                'text-align': 'right',
                'direction': 'rtl'
            }
        }
    
    def apply_rtl_styles(self):
        """Apply RTL CSS styles"""
        st.markdown("""
        <style>
            .rtl-container {
                direction: rtl;
                text-align: right;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .rtl-input input {
                text-align: right;
                direction: rtl;
            }
            
            .rtl-textarea textarea {
                text-align: right;
                direction: rtl;
            }
            
            .arabic-text {
                font-family: 'Segoe UI', 'Microsoft Sans Arabic', 'Arial';
                line-height: 1.8;
                font-size: 16px;
            }
            
            /* RTL Chat message alignment */
            .rtl-chat .stChatMessage {
                text-align: right;
                direction: rtl;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def reshape_arabic_text(self, text: str) -> str:
        """Reshape Arabic text for proper display"""
        try:
            if self._contains_arabic(text):
                reshaped_text = arabic_reshaper.reshape(text)
                return get_display(reshaped_text)
            return text
        except Exception as e:
            st.error(f"Arabic text processing error: {e}")
            return text
    
    def _contains_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        arabic_range = range(0x0600, 0x06FF + 1)
        return any(ord(char) in arabic_range for char in text)
    
    def create_rtl_container(self):
        """Create an RTL container context"""
        return st.container()
    
    def display_bilingual(self, english_text: str, arabic_text: str):
        """Display text in both English and Arabic"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**English:** {english_text}")
        
        with col2:
            st.markdown(
                f"<div class='arabic-text'><strong>العربية:</strong> {self.reshape_arabic_text(arabic_text)}</div>",
                unsafe_allow_html=True
            )
    
    def get_rtl_markdown(self, text: str) -> str:
        """Get RTL formatted markdown"""
        if self._contains_arabic(text):
            return f"<div class='rtl-container arabic-text'>{self.reshape_arabic_text(text)}</div>"
        return text
    
    def create_arabic_input(self, label: str, key: str, placeholder: str = ""):
        """Create an Arabic-friendly text input"""
        st.markdown(f"<div class='rtl-container'><label>{label}</label></div>", 
                   unsafe_allow_html=True)
        
        # Create custom input with RTL styling
        input_style = """
        <style>
            .rtl-input input {
                text-align: right;
                direction: rtl;
                font-family: 'Segoe UI', 'Microsoft Sans Arabic';
            }
        </style>
        """
        st.markdown(input_style, unsafe_allow_html=True)
        
        return st.text_input(
            "",
            key=key,
            placeholder=placeholder,
            label_visibility="collapsed"
        )
    
    def setup_arabic_interface(self, interface_elements: Dict[str, str]):
        """Setup Arabic interface translations"""
        st.session_state.arabic_interface = interface_elements
    
    def get_interface_text(self, key: str, language: str = "both") -> str:
        """Get interface text in specified language"""
        if not hasattr(st.session_state, 'arabic_interface'):
            # Default interface translations
            st.session_state.arabic_interface = {
                'welcome': {
                    'english': 'Welcome to Pearl Lolo AI',
                    'arabic': 'مرحباً بكم في لولو الذكية'
                },
                'ask_question': {
                    'english': 'Ask me anything...',
                    'arabic': 'اسألني أي شيء...'
                },
                'settings': {
                    'english': 'Settings',
                    'arabic': 'الإعدادات'
                },
                'language': {
                    'english': 'Language',
                    'arabic': 'اللغة'
                },
                'upload': {
                    'english': 'Upload Documents',
                    'arabic': 'رفع المستندات'
                },
                'search': {
                    'english': 'Web Search',
                    'arabic': 'البحث على الإنترنت'
                }
            }
        
        if key not in st.session_state.arabic_interface:
            return key
        
        translations = st.session_state.arabic_interface[key]
        
        if language == 'arabic':
            return translations.get('arabic', key)
        elif language == 'english':
            return translations.get('english', key)
        else:
            # Return both languages
            english = translations.get('english', key)
            arabic = translations.get('arabic', key)
            return f"{english} / {arabic}"