#!/usr/bin/env python3
"""
UI Components - Reusable Streamlit components for Pearl Lolo
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from pathlib import Path

class UIComponents:
    def __init__(self):
        self.icons = {
            'ai': '🤖',
            'settings': '⚙️',
            'upload': '📁',
            'search': '🔍',
            'chat': '💬',
            'document': '📄',
            'download': '📥',
            'warning': '⚠️',
            'success': '✅',
            'error': '❌',
            'info': 'ℹ️'
        }
    
    def create_header(self, title: str, subtitle: str = ""):
        """Create application header"""
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #d2cdbd; margin: 0; font-size: 2.5rem;">
                {self.icons['ai']} {title}
            </h1>
            <p style="color: #95b3f4; font-size: 1.2rem; margin: 0;">
                {subtitle}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def create_metric_card(self, title: str, value: str, delta: str = None):
        """Create a glassmorphism metric card"""
        delta_html = ""
        if delta:
            delta_color = "color: #4CAF50;" if delta.startswith("+") else "color: #f44336;"
            delta_html = f'<div style="{delta_color} font-size: 0.9rem;">{delta}</div>'
        
        card_html = f"""
        <div class="glass-container" style="text-align: center; padding: 15px;">
            <div style="font-size: 0.9rem; color: #95b3f4; margin-bottom: 5px;">
                {title}
            </div>
            <div style="font-size: 1.8rem; color: #d2cdbd; font-weight: bold;">
                {value}
            </div>
            {delta_html}
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    
    def create_feature_toggle(self, feature_name: str, default: bool = False) -> bool:
        """Create a stylish feature toggle"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(feature_name)
        
        with col2:
            return st.toggle("", value=default, key=f"toggle_{feature_name}")
    
    def create_progress_with_text(self, label: str, value: float, max_value: float):
        """Create progress bar with text label"""
        progress_html = f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #d2cdbd;">{label}</span>
                <span style="color: #95b3f4;">{value}/{max_value}</span>
            </div>
            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 8px;">
                <div style="background: linear-gradient(90deg, #d2cdbd, #95b3f4); 
                          width: {(value/max_value)*100}%; 
                          height: 100%; 
                          border-radius: 10px;">
                </div>
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
    
    def create_document_uploader(self, allowed_types: List[str] = None):
        """Create enhanced document uploader"""
        if allowed_types is None:
            allowed_types = ['.pdf', '.txt', '.docx', '.pptx', '.xlsx']
        
        st.markdown("### 📁 Document Upload")
        
        uploaded_files = st.file_uploader(
            "Choose files for RAG system",
            type=allowed_types,
            accept_multiple_files=True,
            key="document_uploader"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) ready for processing")
            
            # Show file details
            for file in uploaded_files:
                file_size = len(file.getvalue()) / 1024  # KB
                st.write(f"📄 {file.name} ({file_size:.1f} KB)")
        
        return uploaded_files
    
    def create_model_selector(self, available_models: List[str], current_model: str):
        """Create AI model selector"""
        st.markdown("### 🧠 AI Model")
        
        selected_model = st.selectbox(
            "Select AI Model",
            options=available_models,
            index=available_models.index(current_model) if current_model in available_models else 0,
            key="model_selector"
        )
        
        # Show model info
        if "local" in selected_model:
            st.info("🔒 Local model - Private and offline")
        elif "openai" in selected_model:
            st.warning("🌐 Cloud model - Requires API key")
        
        return selected_model
    
    def create_personality_selector(self, personalities: List[str], current_personality: str):
        """Create personality selector"""
        st.markdown("### 🎭 Personality")
        
        # Create personality cards
        cols = st.columns(len(personalities))
        
        selected_personality = current_personality
        
        for i, personality in enumerate(personalities):
            with cols[i]:
                if st.button(
                    personality,
                    key=f"personality_{personality}",
                    use_container_width=True
                ):
                    selected_personality = personality
        
        return selected_personality
    
    def create_status_indicator(self, status: str, message: str):
        """Create status indicator"""
        status_icons = {
            'loading': '⏳',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        status_colors = {
            'loading': '#FFA500',
            'success': '#4CAF50',
            'error': '#f44336',
            'warning': '#FF9800',
            'info': '#2196F3'
        }
        
        icon = status_icons.get(status, '●')
        color = status_colors.get(status, '#95b3f4')
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 10px; 
                    background: rgba(255,255,255,0.05); border-radius: 10px; 
                    border-left: 4px solid {color};">
            <span style="font-size: 1.2rem; margin-right: 10px;">{icon}</span>
            <span style="color: {color};">{message}</span>
        </div>
        """, unsafe_allow_html=True)
    
    def create_chat_message(self, message: str, is_user: bool = False, timestamp: str = None):
        """Create a chat message bubble"""
        alignment = "flex-end" if is_user else "flex-start"
        background = "rgba(149, 179, 244, 0.3)" if is_user else "rgba(210, 205, 189, 0.3)"
        
        timestamp_html = ""
        if timestamp:
            timestamp_html = f'<div style="font-size: 0.7rem; color: rgba(255,255,255,0.5); margin-top: 5px;">{timestamp}</div>'
        
        chat_html = f"""
        <div style="display: flex; justify-content: {alignment}; margin: 10px 0;">
            <div style="
                background: {background};
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 12px 16px;
                max-width: 70%;
                border: 1px solid rgba(255,255,255,0.2);
            ">
                <div style="color: white; line-height: 1.4;">{message}</div>
                {timestamp_html}
            </div>
        </div>
        """
        st.markdown(chat_html, unsafe_allow_html=True)
    
    def create_api_key_input(self, service_name: str, current_key: str = ""):
        """Create API key input with visibility toggle"""
        st.markdown(f"### 🔑 {service_name} API Key")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            api_key = st.text_input(
                f"{service_name} Key",
                value=current_key,
                type="password",
                placeholder=f"Enter your {service_name} API key...",
                key=f"api_key_{service_name}"
            )
        
        with col2:
            st.write("")  # Spacer
            if st.button("👁️", key=f"toggle_{service_name}"):
                st.session_state[f'show_{service_name}'] = not st.session_state.get(f'show_{service_name}', False)
        
        # Show key in plain text if toggled
        if st.session_state.get(f'show_{service_name}', False):
            st.code(api_key if api_key else "No key entered")
        
        return api_key