"""
Minimal MCP-like Server Implementation using Python Standard Library.

This module provides a simple HTTP server that exposes registered tools
through a REST API compatible with Model Context Protocol patterns.

Endpoints:
- GET /tools: List available tools and their schemas
- POST /call: Execute a tool with provided arguments

Uses only Python standard library (no third-party dependencies).
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional, List, Union
import traceback

from .tools import get_tools, get_registry
from .tools.errors import ToolExecutionError, SchemaValidationError


class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP-like server endpoints."""
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response with proper headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error_response(self, message: str, status_code: int = 400, error_type: str = "error"):
        """Send standardized error response."""
        error_data = {
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code
            }
        }
        self._send_json_response(error_data, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - primarily for /tools endpoint."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/tools':
            self._handle_list_tools()
        elif parsed_path.path == '/' or parsed_path.path == '/health':
            self._handle_health_check()
        else:
            self._send_error_response(f"Endpoint not found: {parsed_path.path}", 404, "not_found")
    
    def do_POST(self):
        """Handle POST requests - primarily for /call endpoint."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/call':
            self._handle_call_tool()
        else:
            self._send_error_response(f"Endpoint not found: {parsed_path.path}", 404, "not_found")
    
    def _handle_health_check(self):
        """Handle health check endpoint."""
        health_data = {
            "status": "healthy",
            "service": "mcp-server",
            "tools_count": get_registry().size()
        }
        self._send_json_response(health_data)
    
    def _handle_list_tools(self):
        """Handle GET /tools - return list of available tools with schemas."""
        try:
            tools = get_tools()
            
            tools_data = []
            for tool in tools:
                tool_info = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
                tools_data.append(tool_info)
            
            response = {
                "tools": tools_data,
                "count": len(tools_data)
            }
            
            self._send_json_response(response)
            
        except Exception as e:
            logging.error(f"Error listing tools: {e}")
            self._send_error_response(f"Failed to list tools: {str(e)}", 500, "internal_error")
    
    def _handle_call_tool(self):
        """Handle POST /call - execute a tool with provided arguments."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error_response("Request body is required", 400, "invalid_request")
                return
            
            request_data = self.rfile.read(content_length)
            
            try:
                call_request = json.loads(request_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                self._send_error_response(f"Invalid JSON in request body: {str(e)}", 400, "invalid_json")
                return
            
            # Validate request structure
            if not isinstance(call_request, dict):
                self._send_error_response("Request body must be a JSON object", 400, "invalid_request")
                return
            
            tool_name = call_request.get('tool')
            arguments = call_request.get('args', {})
            
            if not tool_name:
                self._send_error_response("'tool' field is required", 400, "missing_tool")
                return
            
            # Execute the tool
            result = self._execute_tool(tool_name, arguments)
            
            response = {
                "result": result,
                "tool": tool_name
            }
            
            self._send_json_response(response)
            
        except ToolExecutionError as e:
            self._send_error_response(f"Tool execution failed: {str(e)}", 400, "tool_execution_error")
        except SchemaValidationError as e:
            self._send_error_response(f"Invalid arguments: {str(e)}", 400, "schema_validation_error")
        except Exception as e:
            logging.error(f"Error calling tool: {e}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            self._send_error_response(f"Internal server error: {str(e)}", 500, "internal_error")
    
    def _execute_tool(self, tool_name: str, arguments: Union[Dict[str, Any], List]) -> Any:
        """Execute a registered tool with given arguments."""
        registry = get_registry()
        
        if not registry.has_tool(tool_name):
            raise ToolExecutionError(f"Tool '{tool_name}' not found", tool_name=tool_name)
        
        tool = registry.get_tool(tool_name)
        
        # Handle both dict and list argument formats
        if isinstance(arguments, list):
            # Convert positional arguments to function call
            return tool.function(*arguments)
        elif isinstance(arguments, dict):
            # Use dict arguments directly
            return tool.call(arguments)
        else:
            raise SchemaValidationError(f"Arguments must be dict or list, got {type(arguments).__name__}")
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        logging.info(f"{self.address_string()} - {format % args}")


class MCPServer:
    """MCP-like server for exposing registered tools via HTTP."""
    
    def __init__(self, host: str = 'localhost', port: int = 8000):
        """Initialize MCP server.
        
        Args:
            host: Server host address
            port: Server port number
        """
        self.host = host
        self.port = port
        self.server = None
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('MCPServer')
    
    def start(self, blocking: bool = True):
        """Start the MCP server.
        
        Args:
            blocking: If True, run server indefinitely. If False, return immediately.
        """
        try:
            self.server = HTTPServer((self.host, self.port), MCPRequestHandler)
            self.logger.info(f"MCP Server starting on http://{self.host}:{self.port}")
            self.logger.info(f"Endpoints available:")
            self.logger.info(f"  GET  /tools  - List available tools")
            self.logger.info(f"  POST /call   - Execute a tool")
            self.logger.info(f"  GET  /health - Health check")
            
            tool_count = get_registry().size()
            self.logger.info(f"Server has {tool_count} registered tools")
            
            if blocking:
                self.server.serve_forever()
            
        except KeyboardInterrupt:
            self.logger.info("Server interrupted by user")
            self.stop()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
    
    def stop(self):
        """Stop the MCP server."""
        if self.server:
            self.logger.info("Stopping MCP Server...")
            self.server.shutdown()
            self.server.server_close()
            self.server = None
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and status."""
        return {
            "host": self.host,
            "port": self.port,
            "running": self.server is not None,
            "tools_count": get_registry().size(),
            "endpoints": [
                {"method": "GET", "path": "/tools", "description": "List available tools"},
                {"method": "POST", "path": "/call", "description": "Execute a tool"},
                {"method": "GET", "path": "/health", "description": "Health check"}
            ]
        }


def create_server(host: str = 'localhost', port: int = 8000) -> MCPServer:
    """Create and return an MCP server instance.
    
    Args:
        host: Server host address
        port: Server port number
        
    Returns:
        MCPServer instance
    """
    return MCPServer(host, port)


def run_server(host: str = 'localhost', port: int = 8000):
    """Run MCP server with registered tools.
    
    Args:
        host: Server host address  
        port: Server port number
    """
    server = create_server(host, port)
    try:
        server.start(blocking=True)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    # Example usage when run directly
    import sys
    
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    run_server(host, port)