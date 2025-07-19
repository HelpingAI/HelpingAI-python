"""
Web Search Tool for HelpingAI SDK

This tool provides web search functionality using Snapzion Search API,
inspired by Qwen-Agent's WebSearch tool.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional, List

from .base import BuiltinToolBase
from ..errors import ToolExecutionError


class WebSearchTool(BuiltinToolBase):
    """Advanced web search tool using Snapzion Search API.
    
    This tool allows searching the web for real-time information with high-quality
    results including titles, snippets, links, and source information.
    """
    
    name = "web_search"
    description = "Search the web for real-time information using advanced search API. Returns comprehensive search results with titles, snippets, links, and source information."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "Search query to look up on the web"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of search results to return (default: 5, max: 10)",
                "default": 5,
                "minimum": 1,
                "maximum": 10
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
        """Execute web search using Snapzion Search API.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: 5, max: 10)
            
        Returns:
            Formatted search results with titles, snippets, links, and sources
        """
        self._validate_parameters(kwargs)
        query = kwargs['query']
        max_results = min(kwargs.get('max_results', 5), 10)  # Cap at 10 results
        
        if not query.strip():
            return "No search query provided."
        
        try:
            # Perform the search using Snapzion API
            results = self._search_snapzion(query, max_results)
            
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
    
    def _search_snapzion(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Snapzion Search API.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            # Snapzion Search API endpoint
            url = 'https://search.snapzion.com/get-snippets'
            
            # Prepare the request data
            data = json.dumps({"query": query}).encode('utf-8')
            
            # Create the request
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'HelpingAI-SDK/1.0'
                },
                method='POST'
            )
            
            # Make the request
            with urllib.request.urlopen(req, timeout=15) as response:
                response_data = json.loads(response.read().decode())
            
            # Extract organic results
            organic_results = response_data.get('organic_results', [])
            
            results = []
            for result in organic_results[:max_results]:
                formatted_result = {
                    'title': result.get('title', 'No title'),
                    'snippet': result.get('snippet', 'No description available'),
                    'url': result.get('link', ''),
                    'source': result.get('source', 'Unknown'),
                    'position': result.get('position', 0)
                }
                results.append(formatted_result)
            
            return results
            
        except Exception as e:
            # Fallback to a simple error result
            return [{
                'title': f'Search Error: {query}',
                'snippet': f'Unable to perform web search. Error: {str(e)}. Please try again or rephrase your query.',
                'url': '',
                'source': 'System',
                'position': 1
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
        
        formatted = [f"Web search results for: '{query}'\n"]
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description available')
            url = result.get('url', '')
            source = result.get('source', 'Unknown')
            position = result.get('position', i)
            
            formatted.append(f"{i}. **{title}**")
            formatted.append(f"   {snippet}")
            if url:
                formatted.append(f"   🔗 URL: {url}")
            formatted.append(f"   📍 Source: {source}")
            if position:
                formatted.append(f"   📊 Position: #{position}")
            formatted.append("")  # Empty line for separation
        
        return "\n".join(formatted)
