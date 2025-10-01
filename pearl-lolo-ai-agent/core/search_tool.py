#!/usr/bin/env python3
"""
Search Tool - Web search capabilities for Pearl Lolo
"""

import os
import requests
from typing import List, Dict, Optional
from googlesearch import search as google_search
from bs4 import BeautifulSoup
import time

class SearchTool:
    def __init__(self, config_manager):
        self.config = config_manager
        self.google_api_key = self.config.get('search.api_key', '')
        self.search_engine_id = self.config.get('search.search_engine_id', '')
    
    def search(self, query: str, num_results: int = 5) -> str:
        """Perform web search and return formatted results"""
        if not self.config.get('search.enabled', False):
            return ""
        
        try:
            # Try Google Custom Search API first
            if self.google_api_key and self.search_engine_id:
                results = self._google_api_search(query, num_results)
            else:
                # Fallback to regular Google search
                results = self._regular_google_search(query, num_results)
            
            # Format results
            formatted_results = self._format_search_results(results, query)
            return formatted_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return f"Search unavailable: {str(e)}"
    
    def _google_api_search(self, query: str, num_results: int) -> List[Dict]:
        """Search using Google Custom Search API"""
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            'key': self.google_api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(num_results, 10)
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })
        
        return results
    
    def _regular_google_search(self, query: str, num_results: int) -> List[Dict]:
        """Search using regular Google search (fallback)"""
        results = []
        
        try:
            search_results = google_search(
                query, 
                num_results=num_results,
                lang='en'
            )
            
            for url in search_results:
                try:
                    # Get page content
                    content = self._extract_page_content(url)
                    
                    results.append({
                        'title': self._extract_title_from_url(url),
                        'link': url,
                        'snippet': content[:200] + "..." if len(content) > 200 else content
                    })
                    
                    # Be polite to servers
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"⚠️  Could not process {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Google search failed: {e}")
        
        return results
    
    def _extract_page_content(self, url: str) -> str:
        """Extract main content from a web page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:500]  # Return first 500 characters
            
        except Exception as e:
            return f"Could not retrieve content: {str(e)}"
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a title from URL"""
        try:
            # Use the domain and path as title
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            path = parsed.path.replace('/', ' ').strip()
            
            if path:
                return f"{domain} - {path}"
            else:
                return domain
                
        except:
            return "Unknown Source"
    
    def _format_search_results(self, results: List[Dict], original_query: str) -> str:
        """Format search results into a readable string"""
        if not results:
            return "No relevant search results found."
        
        formatted = f"🔍 Search Results for: '{original_query}'\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result['title']}**\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   📎 {result['link']}\n\n"
        
        return formatted
    
    def validate_api_keys(self) -> bool:
        """Validate that API keys are working"""
        if not self.google_api_key or not self.search_engine_id:
            return False
        
        try:
            # Test the API with a simple query
            test_results = self._google_api_search("test", 1)
            return len(test_results) > 0
        except:
            return False