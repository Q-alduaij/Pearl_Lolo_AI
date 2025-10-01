#!/usr/bin/env python3
"""
Pearl Lolo AI Agent - FIXED Main Application
"""

import os
import sys
import streamlit as st
from pathlib import Path
import logging

# Add core directory to path
core_dir = Path(__file__).parent / "core"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

try:
    from config_manager import ConfigManager
    from ai_engine import AIEngine
    from rag_system import RAGSystem
    from search_tool import SearchTool
    from personality_engine import PersonalityEngine
    from bilingual_processor import BilingualProcessor
except ImportError as e:
    st.error(f"❌ Failed to import core modules: {e}")
    st.stop()

class PearlLoloApp:
    def __init__(self):
        # Initialize configuration first
        self.config = ConfigManager()
        
        # Initialize core components with error handling
        try:
            self.ai_engine = AIEngine(self.config)
            self.rag_system = RAGSystem(self.config)
            self.search_tool = SearchTool(self.config)
            self.personality = PersonalityEngine(self.config)
            self.bilingual_processor = BilingualProcessor()
        except Exception as e:
            st.error(f"❌ Failed to initialize components: {e}")
            st.stop()
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'documents_processed' not in st.session_state:
            st.session_state.documents_processed = []
        
        if 'current_personality' not in st.session_state:
            st.session_state.current_personality = 'lolo'
    
    def setup_streamlit(self):
        """Configure Streamlit page with error handling"""
        try:
            st.set_page_config(
                page_title="Pearl Lolo AI Agent",
                page_icon="🤖",
                layout="wide",
                initial_sidebar_state="expanded"
            )
            
            # Apply custom CSS
            self.apply_custom_css()
            
        except Exception as e:
            st.error(f"❌ Streamlit setup failed: {e}")
    
    def apply_custom_css(self):
        """Apply custom CSS styles"""
        try:
            css_file = Path(__file__).parent / "static" / "css" / "glassmorphism.css"
            if css_file.exists():
                with open(css_file, 'r', encoding='utf-8') as f:
                    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            else:
                # Fallback inline CSS
                st.markdown("""
                <style>
                .stApp { background: linear-gradient(135deg, rgba(210,205,189,0.1) 0%, rgba(149,179,244,0.1) 100%); }
                </style>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ CSS loading failed: {e}")
    
    def render_sidebar(self):
        """Render sidebar with configuration options"""
        with st.sidebar:
            st.title("🧠 Pearl Lolo")
            
            # Language selection
            language = st.selectbox(
                "Language",
                ["English", "Arabic", "Both"],
                index=2,
                key="language_select"
            )
            
            # AI Model selection
            model_options = self.ai_engine.get_available_models()
            selected_model = st.selectbox(
                "AI Model",
                options=model_options,
                index=0,
                key="model_select"
            )
            
            # Personality selection
            personality_options = self.personality.get_available_personalities()
            current_personality = st.selectbox(
                "Personality",
                options=personality_options,
                index=personality_options.index(st.session_state.current_personality) 
                if st.session_state.current_personality in personality_options else 0,
                key="personality_select"
            )
            
            # Update personality if changed
            if current_personality != st.session_state.current_personality:
                st.session_state.current_personality = current_personality
                self.personality.set_personality(current_personality)
            
            # Feature toggles
            col1, col2 = st.columns(2)
            with col1:
                rag_enabled = st.checkbox("RAG", value=True, key="rag_toggle")
            with col2:
                search_enabled = st.checkbox("Web Search", value=False, key="search_toggle")
            
            # API Settings
            with st.expander("🔑 API Settings", expanded=False):
                openai_key = st.text_input("OpenAI Key", type="password", 
                                         value=self.config.get('ai.models.openai.api_key', ''))
                google_key = st.text_input("Google Search Key", type="password",
                                         value=self.config.get('search.api_key', ''))
                
                if st.button("Save API Keys"):
                    updates = {
                        'ai.models.openai.api_key': openai_key,
                        'search.api_key': google_key
                    }
                    if self.config.update_batch(updates):
                        st.success("API keys saved!")
                    else:
                        st.error("Failed to save API keys")
            
            # System Info
            with st.expander("ℹ️ System Info", expanded=False):
                st.write(f"Models loaded: {len(self.ai_engine.get_loaded_models())}")
                st.write(f"Documents in RAG: {self.rag_system.get_document_count()}")
                
                if st.button("Clear Chat History"):
                    st.session_state.messages = []
                    st.rerun()
    
    def render_chat_interface(self):
        """Render main chat interface"""
        st.title("💬 Pearl Lolo AI Assistant")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything in English or Arabic..."):
            self._process_user_input(prompt)
    
    def _process_user_input(self, prompt: str):
        """Process user input and generate response"""
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = self._generate_ai_response(prompt)
                    st.markdown(response)
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    def _generate_ai_response(self, prompt: str) -> str:
        """Generate AI response using all available systems"""
        # Get context from RAG if enabled
        context = ""
        if st.session_state.get('rag_toggle', True):
            context = self.rag_system.get_relevant_context(prompt)
        
        # Get web search results if enabled
        search_results = ""
        if st.session_state.get('search_toggle', False):
            search_results = self.search_tool.search(prompt)
        
        # Generate response
        response = self.ai_engine.generate_response(
            prompt=prompt,
            context=context,
            search_results=search_results,
            personality=st.session_state.current_personality
        )
        
        return response
    
    def render_document_upload(self):
        """Render document upload section for RAG"""
        with st.expander("📁 Upload Documents for RAG", expanded=False):
            uploaded_files = st.file_uploader(
                "Choose files to add to knowledge base",
                type=['pdf', 'txt', 'docx', 'pptx', 'xlsx', 'csv'],
                accept_multiple_files=True,
                key="document_uploader"
            )
            
            if uploaded_files and st.button("Process Documents"):
                self._process_uploaded_files(uploaded_files)
            
            # Show processed documents
            if st.session_state.documents_processed:
                st.write("**Processed Documents:**")
                for doc in st.session_state.documents_processed[-5:]:  # Show last 5
                    st.write(f"📄 {doc}")
    
    def _process_uploaded_files(self, uploaded_files):
        """Process and add uploaded files to RAG system"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save file temporarily
                temp_path = Path("temp") / uploaded_file.name
                temp_path.parent.mkdir(exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Add to RAG system
                if self.rag_system.add_document(str(temp_path)):
                    st.session_state.documents_processed.append(uploaded_file.name)
                    st.success(f"✅ Added: {uploaded_file.name}")
                else:
                    st.error(f"❌ Failed to process: {uploaded_file.name}")
                
                # Cleanup temp file
                if temp_path.exists():
                    temp_path.unlink()
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("Document processing complete!")
    
    def run(self):
        """Run the main application"""
        try:
            self.setup_streamlit()
            self.render_sidebar()
            self.render_document_upload()
            self.render_chat_interface()
            
        except Exception as e:
            st.error(f"❌ Application error: {e}")
            st.info("Please check the logs for more details.")

def main():
    """Main entry point with error handling"""
    try:
        # Ensure required directories exist
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        Path("temp").mkdir(exist_ok=True)
        
        app = PearlLoloApp()
        app.run()
        
    except Exception as e:
        st.error(f"🚨 Critical error starting application: {e}")
        st.stop()

if __name__ == "__main__":
    main()