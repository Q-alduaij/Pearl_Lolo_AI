#!/usr/bin/env python3
"""
AI Engine - FIXED VERSION with proper error handling
"""

import os
import logging
from typing import Dict, List, Optional

class AIEngine:
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.current_model = None
        
        # Initialize model clients with error handling
        self.setup_clients()
    
    def setup_clients(self):
        """Setup AI clients with proper error handling"""
        self.ollama_client = None
        self.anthropic_client = None
        
        try:
            # Ollama client
            import ollama
            ollama_host = self.config.get('ai.models.local.base_url', 'http://localhost:11434')
            self.ollama_client = ollama.Client(host=ollama_host)
            self.logger.info("Ollama client initialized")
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
        
        try:
            # OpenAI client
            openai_api_key = self.config.get('ai.models.openai.api_key')
            if openai_api_key:
                import openai
                openai.api_key = openai_api_key
                self.logger.info("OpenAI client initialized")
        except Exception as e:
            self.logger.warning(f"OpenAI setup failed: {e}")
        
        try:
            # Anthropic client
            anthropic_api_key = self.config.get('ai.models.anthropic.api_key')
            if anthropic_api_key:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
                self.logger.info("Anthropic client initialized")
        except Exception as e:
            self.logger.warning(f"Anthropic setup failed: {e}")
        
        try:
            # Google AI client
            google_api_key = self.config.get('ai.models.google.api_key')
            if google_api_key:
                import google.generativeai as genai
                genai.configure(api_key=google_api_key)
                self.logger.info("Google AI client initialized")
        except Exception as e:
            self.logger.warning(f"Google AI setup failed: {e}")
    
    def generate_response(self, 
                         prompt: str, 
                         context: str = "", 
                         search_results: str = "",
                         personality: str = "lolo",
                         max_tokens: int = 1500) -> str:
        """Generate response with comprehensive error handling"""
        
        # Build enhanced prompt
        enhanced_prompt = self._build_enhanced_prompt(
            prompt, context, search_results, personality
        )
        
        # Get model provider
        provider = self.config.get('ai.default_model', 'local')
        
        try:
            if provider == 'local':
                return self._generate_local(enhanced_prompt, max_tokens)
            elif provider == 'openai':
                return self._generate_openai(enhanced_prompt, max_tokens)
            elif provider == 'anthropic':
                return self._generate_anthropic(enhanced_prompt, max_tokens)
            elif provider == 'google':
                return self._generate_google(enhanced_prompt, max_tokens)
            else:
                return self._generate_fallback(enhanced_prompt)
                
        except Exception as e:
            self.logger.error(f"AI generation error: {e}")
            return f"❌ I encountered an error while generating a response: {str(e)}"
    
    def _build_enhanced_prompt(self, prompt: str, context: str, 
                              search_results: str, personality: str) -> str:
        """Build enhanced prompt with proper formatting"""
        
        personality_profile = self.config.get(f'personality.profiles.{personality}', {})
        tone = personality_profile.get('tone', 'friendly')
        response_style = personality_profile.get('response_style', 'detailed')
        
        system_prompt = f"""You are {personality}, an AI assistant with the following characteristics:
- Tone: {tone}
- Response Style: {response_style}
- Language: Bilingual (Arabic/English)
- Personality: Helpful, knowledgeable, and engaging

Context Information:
"""
        if context:
            system_prompt += f"{context}\n\n"
        else:
            system_prompt += "No specific context available.\n\n"
        
        if search_results:
            system_prompt += f"Search Results:\n{search_results}\n\n"
        
        system_prompt += f"User Question: {prompt}\n\nResponse:"
        
        return system_prompt
    
    def _generate_local(self, prompt: str, max_tokens: int) -> str:
        """Generate using local Ollama with proper error handling"""
        if not self.ollama_client:
            return "❌ Local AI service (Ollama) is not available. Please install and start Ollama."
        
        try:
            model = self.config.get('ai.models.local.model', 'llama2')
            
            # Check if model is available
            try:
                models = self.ollama_client.list()
                available_models = [m['name'] for m in models.get('models', [])]
                
                if not any(model in available_model for available_model in available_models):
                    return f"❌ Model '{model}' not found. Please pull it with: ollama pull {model}"
            except:
                return "❌ Cannot connect to Ollama. Please ensure it's running."
            
            response = self.ollama_client.generate(
                model=model,
                prompt=prompt,
                options={
                    'num_predict': max_tokens,
                    'temperature': 0.7,
                    'top_p': 0.9
                }
            )
            return response['response']
            
        except Exception as e:
            return f"❌ Local AI error: {str(e)}"
    
    def _generate_openai(self, prompt: str, max_tokens: int) -> str:
        """Generate using OpenAI API"""
        try:
            import openai
            
            model = self.config.get('ai.models.openai.model', 'gpt-3.5-turbo')
            api_key = self.config.get('ai.models.openai.api_key')
            
            if not api_key:
                return "❌ OpenAI API key not configured. Please add it in settings."
            
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ OpenAI error: {str(e)}"
    
    def _generate_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Generate using Anthropic Claude"""
        if not self.anthropic_client:
            return "❌ Anthropic API key not configured"
        
        try:
            model = self.config.get('ai.models.anthropic.model', 'claude-3-sonnet-20240229')
            
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
            
        except Exception as e:
            return f"❌ Anthropic error: {str(e)}"
    
    def _generate_google(self, prompt: str, max_tokens: int) -> str:
        """Generate using Google AI"""
        try:
            import google.generativeai as genai
            
            model = self.config.get('ai.models.google.model', 'gemini-pro')
            api_key = self.config.get('ai.models.google.api_key')
            
            if not api_key:
                return "❌ Google AI API key not configured"
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model)
            response = model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            return f"❌ Google AI error: {str(e)}"
    
    def _generate_fallback(self, prompt: str) -> str:
        """Fallback response"""
        return """🤖 Pearl Lolo AI Assistant

I'm currently having trouble connecting to my AI services. Here's what you can check:

**For Local AI (Ollama):**
1. Install Ollama: https://ollama.ai
2. Start the service: `ollama serve`
3. Pull a model: `ollama pull llama2`

**For Cloud AI Services:**
1. Add your API keys in the settings panel
2. Ensure you have internet connectivity
3. Check your API quota and billing

**Quick Setup for Local Use:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
ollama serve

# Download model (in new terminal)
ollama pull llama2