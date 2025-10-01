#!/usr/bin/env python3
"""
Glassmorphism Theme - Modern transparent UI design for Pearl Lolo
"""

import streamlit as st
from typing import Dict, Any

class GlassmorphismTheme:
    def __init__(self):
        self.primary_color = "#d2cdbd"
        self.secondary_color = "#95b3f4"
        self.background_color = "rgba(255, 255, 255, 0.1)"
        self.blur_amount = "blur(10px)"
        self.border_radius = "15px"
        
    def apply_theme(self):
        """Apply glassmorphism theme to Streamlit"""
        st.markdown(f"""
        <style>
            /* Global Styles */
            .stApp {{
                background: linear-gradient(135deg, 
                    rgba(210, 205, 189, 0.1) 0%, 
                    rgba(149, 179, 244, 0.1) 100%);
                background-attachment: fixed;
            }}
            
            /* Glassmorphism Containers */
            .glass-container {{
                background: {self.background_color};
                backdrop-filter: {self.blur_amount};
                -webkit-backdrop-filter: {self.blur_amount};
                border-radius: {self.border_radius};
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }}
            
            /* Sidebar Glass Effect */
            .css-1d391kg {{
                background: {self.background_color} !important;
                backdrop-filter: {self.blur_amount} !important;
                -webkit-backdrop-filter: {self.blur_amount} !important;
                border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
            }}
            
            /* Chat Messages */
            .stChatMessage {{
                background: {self.background_color} !important;
                backdrop-filter: {self.blur_amount} !important;
                -webkit-backdrop-filter: {self.blur_amount} !important;
                border-radius: {self.border_radius} !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                padding: 15px !important;
                margin: 5px 0 !important;
            }}
            
            /* Buttons */
            .stButton>button {{
                background: {self.background_color} !important;
                backdrop-filter: {self.blur_amount} !important;
                -webkit-backdrop-filter: {self.blur_amount} !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: {self.border_radius} !important;
                color: {self.primary_color} !important;
                font-weight: 500 !important;
            }}
            
            .stButton>button:hover {{
                background: rgba(210, 205, 189, 0.3) !important;
                border: 1px solid {self.primary_color} !important;
                transform: translateY(-2px);
                transition: all 0.3s ease;
            }}
            
            /* Input Fields */
            .stTextInput>div>div>input {{
                background: {self.background_color} !important;
                backdrop-filter: {self.blur_amount} !important;
                -webkit-backdrop-filter: {self.blur_amount} !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: {self.border_radius} !important;
                color: white !important;
            }}
            
            /* Select Boxes */
            .stSelectbox>div>div {{
                background: {self.background_color} !important;
                backdrop-filter: {self.blur_amount} !important;
                -webkit-backdrop-filter: {self.blur_amount} !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: {self.border_radius} !important;
            }}
            
            /* Expanders */
            .streamlit-expanderHeader {{
                background: {self.background_color} !important;
                backdrop-filter: {self.blur_amount} !important;
                -webkit-backdrop-filter: {self.blur_amount} !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: {self.border_radius} !important;
            }}
            
            /* Progress Bars */
            .stProgress > div > div > div {{
                background: linear-gradient(90deg, 
                    {self.primary_color} 0%, 
                    {self.secondary_color} 100%) !important;
            }}
            
            /* RTL Support for Arabic */
            .rtl-text {{
                direction: rtl;
                text-align: right;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {self.primary_color};
                border-radius: 10px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {self.secondary_color};
            }}
            
            /* Animation for loading */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .fade-in {{
                animation: fadeIn 0.5s ease-in;
            }}
            
            /* Mobile Responsive */
            @media (max-width: 768px) {{
                .glass-container {{
                    padding: 15px;
                    margin: 5px 0;
                }}
                
                .stChatMessage {{
                    padding: 10px !important;
                }}
            }}
        </style>
        """, unsafe_allow_html=True)
    
    def create_glass_card(self, content: str, class_name: str = "") -> str:
        """Create a glassmorphism card with content"""
        return f"""
        <div class="glass-container {class_name}">
            {content}
        </div>
        """
    
    def apply_custom_colors(self, primary: str = None, secondary: str = None):
        """Apply custom color scheme"""
        if primary:
            self.primary_color = primary
        if secondary:
            self.secondary_color = secondary
        
        self.apply_theme()