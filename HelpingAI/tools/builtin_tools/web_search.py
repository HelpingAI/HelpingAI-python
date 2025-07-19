"""
Web Search Tool for HelpingAI SDK

This tool provides web search functionality using DuckDuckGo's API,
inspired by Qwen-Agent's WebSearch tool.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional, List

from .base import BuiltinToolBase
from ..errors import ToolExecutionError


class WebSearchTool(BuiltinToolBase):
    """Web search tool using DuckDuckGo API.
    
    This tool allows searching the web for information using DuckDuckGo's
    instant answer API, which doesn't require an API key.
    """
    
    name = "web_search"
    description = "Search the web for information using DuckDuckGo. Returns search results with titles, snippets, and URLs."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "Search query to look up"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the web search tool.
        
        Args:
            config: Optional configuration dict
        """
        super().__init__(config)
    
    def execute(self, **kwargs) -> str:
        """Execute web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: 5)
            
        Returns:
            Formatted search results
        """
        self._validate_parameters(kwargs)
        query = kwargs['query']
        max_results = kwargs.get('max_results', 5)
        
        if not query.strip():
            return "No search query provided."
        
        try:
            # Perform the search
            results = self._search_duckduckgo(query, max_results)
            
            if not results:
                return f"No search results found for query: {query}"
            
            # Format results
            formatted_results = self._format_results(results, query)
            return formatted_results
            
        except Exception as e:
            raise ToolExecutionError(
                f"Web search failed: {e}",
                tool_name=self.name,
                original_error=e
            )
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo's instant answer API.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            # Use DuckDuckGo's instant answer API
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            # Make the request
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            results = []
            
            # Get abstract/definition if available
            if data.get('Abstract'):
                results.append({
                    'title': data.get('AbstractText', query),
                    'snippet': data.get('Abstract', ''),
                    'url': data.get('AbstractURL', ''),
                    'source': data.get('AbstractSource', 'DuckDuckGo')
                })
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:max_results-len(results)]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' ') or 'Related Topic',
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'Wikipedia'
                    })
            
            # Get instant answer if available
            if data.get('Answer') and len(results) < max_results:
                results.insert(0, {
                    'title': 'Instant Answer',
                    'snippet': data.get('Answer', ''),
                    'url': data.get('AnswerURL', ''),
                    'source': 'DuckDuckGo'
                })
            
            return results[:max_results]
            
        except Exception as e:
            # Fallback to a simple search result
            return [{
                'title': f'Search: {query}',
                'snippet': f'Sorry, unable to perform web search at this time. Error: {str(e)}',
                'url': f'https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}',
                'source': 'DuckDuckGo'
            }]
    
    def _format_results(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format search results for display.
        
        Args:
            results: List of search result dictionaries
            query: Original search query
            
        Returns:
            Formatted results string
        """
        if not results:
            return f"No results found for: {query}"
        
        formatted = [f"Web search results for: {query}\n"]
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description available')
            url = result.get('url', '')
            source = result.get('source', 'Unknown')
            
            formatted.append(f"{i}. **{title}**")
            formatted.append(f"   {snippet}")
            if url:
                formatted.append(f"   URL: {url}")
            formatted.append(f"   Source: {source}")
            formatted.append("")  # Empty line for separation
        
        return "\n".join(formatted)
    
    def _search_fallback(self, query: str) -> List[Dict[str, Any]]:
        """Fallback search method when main API fails.
        
        Args:
            query: Search query
            
        Returns:
            Fallback result
        """
        return [{
            'title': f'Search: {query}',
            'snippet': 'Web search functionality is currently limited. Try searching manually.',
            'url': f'https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}',
            'source': 'DuckDuckGo'
        }]