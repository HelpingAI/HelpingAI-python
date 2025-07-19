"""
Minimal MCP-like Client Implementation using Python Standard Library.

This module provides a simple HTTP client for interacting with MCP-like servers
that expose tools through REST API endpoints.

Uses only Python standard library (no third-party dependencies).
"""

import json
import logging
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from typing import Dict, Any, List, Optional, Union


class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass


class MCPConnectionError(MCPClientError):
    """Error connecting to MCP server."""
    pass


class MCPServerError(MCPClientError):
    """Error response from MCP server."""
    
    def __init__(self, message: str, status_code: int = None, error_type: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type


class MCPClient:
    """Client for interacting with MCP-like servers."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """Initialize MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('MCPClient')
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to MCP server.
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            data: Request data for POST requests
            
        Returns:
            Parsed JSON response
            
        Raises:
            MCPConnectionError: If connection fails
            MCPServerError: If server returns an error
        """
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        try:
            # Prepare request
            if method.upper() == 'GET':
                req = Request(url, method='GET')
            elif method.upper() == 'POST':
                req_data = json.dumps(data).encode('utf-8') if data else b''
                req = Request(url, data=req_data, method='POST')
                req.add_header('Content-Type', 'application/json')
            else:
                raise MCPClientError(f"Unsupported HTTP method: {method}")
            
            req.add_header('User-Agent', 'MCPClient/1.0')
            
            # Make request
            with urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
                
        except HTTPError as e:
            # Handle HTTP errors from server
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                if 'error' in error_data:
                    error_info = error_data['error']
                    raise MCPServerError(
                        error_info.get('message', str(e)),
                        status_code=e.code,
                        error_type=error_info.get('type', 'unknown')
                    )
                else:
                    raise MCPServerError(f"HTTP {e.code}: {e.reason}", status_code=e.code)
            except (json.JSONDecodeError, KeyError):
                raise MCPServerError(f"HTTP {e.code}: {e.reason}", status_code=e.code)
                
        except URLError as e:
            raise MCPConnectionError(f"Failed to connect to server: {e}")
        except json.JSONDecodeError as e:
            raise MCPClientError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise MCPClientError(f"Request failed: {e}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from the server.
        
        Returns:
            List of tool definitions with name, description, and parameters
        """
        try:
            response = self._make_request('GET', '/tools')
            tools = response.get('tools', [])
            
            self.logger.info(f"Retrieved {len(tools)} tools from server")
            return tools
            
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            raise
    
    def call_tool(self, tool_name: str, arguments: Union[Dict[str, Any], List] = None) -> Any:
        """Call a tool on the server with provided arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments (dict or list)
            
        Returns:
            Tool execution result
        """
        if arguments is None:
            arguments = {}
        
        call_data = {
            "tool": tool_name,
            "args": arguments
        }
        
        try:
            response = self._make_request('POST', '/call', call_data)
            result = response.get('result')
            
            self.logger.info(f"Successfully called tool '{tool_name}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to call tool '{tool_name}': {e}")
            raise
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information dict or None if tool not found
        """
        tools = self.list_tools()
        
        for tool in tools:
            if tool.get('name') == tool_name:
                return tool
        
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health and status.
        
        Returns:
            Server health information
        """
        try:
            return self._make_request('GET', '/health')
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            raise
    
    def ping(self) -> bool:
        """Simple ping to check if server is reachable.
        
        Returns:
            True if server is reachable, False otherwise
        """
        try:
            self.health_check()
            return True
        except Exception:
            return False
    
    def discover_tools(self) -> Dict[str, Dict[str, Any]]:
        """Discover all tools and return as a mapping for easy access.
        
        Returns:
            Dict mapping tool names to tool information
        """
        tools_list = self.list_tools()
        return {tool['name']: tool for tool in tools_list}
    
    def tool_exists(self, tool_name: str) -> bool:
        """Check if a specific tool exists on the server.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool exists, False otherwise
        """
        return self.get_tool_info(tool_name) is not None
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get comprehensive server information.
        
        Returns:
            Dictionary with server details and capabilities
        """
        try:
            health = self.health_check()
            tools = self.list_tools()
            
            return {
                "base_url": self.base_url,
                "status": health.get('status', 'unknown'),
                "tools_count": len(tools),
                "tools": [tool['name'] for tool in tools],
                "server_info": health
            }
        except Exception as e:
            return {
                "base_url": self.base_url,
                "status": "unreachable",
                "error": str(e)
            }


def create_client(base_url: str = "http://localhost:8000", timeout: int = 30) -> MCPClient:
    """Create and return an MCP client instance.
    
    Args:
        base_url: Base URL of the MCP server
        timeout: Request timeout in seconds
        
    Returns:
        MCPClient instance
    """
    return MCPClient(base_url, timeout)


def quick_call(tool_name: str, arguments: Union[Dict[str, Any], List] = None, 
               server_url: str = "http://localhost:8000") -> Any:
    """Quick function to call a tool without creating a client instance.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments
        server_url: MCP server URL
        
    Returns:
        Tool execution result
    """
    client = create_client(server_url)
    return client.call_tool(tool_name, arguments)


def list_remote_tools(server_url: str = "http://localhost:8000") -> List[Dict[str, Any]]:
    """Quick function to list tools from server.
    
    Args:
        server_url: MCP server URL
        
    Returns:
        List of available tools
    """
    client = create_client(server_url)
    return client.list_tools()


if __name__ == "__main__":
    # Example usage when run directly
    import sys
    
    # Parse command line arguments
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    client = create_client(server_url)
    
    print(f"Connecting to MCP server at {server_url}")
    
    try:
        # Test connection
        if client.ping():
            print("✓ Server is reachable")
            
            # Get server info
            info = client.get_server_info()
            print(f"✓ Server status: {info['status']}")
            print(f"✓ Available tools: {info['tools_count']}")
            
            # List tools
            tools = client.list_tools()
            if tools:
                print("\nAvailable tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
            else:
                print("\nNo tools available on server")
        else:
            print("✗ Server is not reachable")
            
    except Exception as e:
        print(f"✗ Error: {e}")