"""Main HAI client class for the HelpingAI platform.

This is the main entry point for interacting with the HelpingAI API.
"""

import json
from typing import Optional, Dict, Any, Union, List

from .base import BaseClient
from .chat import Chat
from ..models import Models


class HAI(BaseClient):
    """HAI API client for the HelpingAI platform.

    This is the main entry point for interacting with the HelpingAI API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        """Initialize HAI client.

        Args:
            api_key: Your API key. Find it at https://helpingai.co/dashboard
            organization: Optional organization ID for API requests
            base_url: Override the default API base URL
            timeout: Timeout for API requests in seconds
        """
        super().__init__(api_key, organization, base_url, timeout)
        self.chat: Chat = Chat(self)
        self.models: Models = Models(self)
        self._tools_config: Optional[Union[List[Dict[str, Any]], List, str]] = None
        self._last_chat_tools_config: Optional[Union[List[Dict[str, Any]], List, str]] = None
        self._mcp_manager = None
        
    def configure_tools(self, tools: Optional[Union[List[Dict[str, Any]], List, str]]) -> None:
        """Configure tools for this client instance.
        
        This makes tools available for direct calling via client.call().
        
        Args:
            tools: Tools configuration in any supported format:
                - List containing MCP server configs, built-in tool names, OpenAI format tools
                - String identifier for built-in tools
                - None to clear tools configuration
                
        Example:
            client.configure_tools([
                {'mcpServers': {
                    'time': {'command': 'uvx', 'args': ['mcp-server-time']},
                    'fetch': {'command': 'uvx', 'args': ['mcp-server-fetch']}
                }},
                'code_interpreter',
                'web_search'
            ])
        """
        self._tools_config = tools
        # Clear cached MCP manager to force reinitialization
        self._mcp_manager = None
        # Clear cached chat tools since we're explicitly configuring tools
        self._last_chat_tools_config = None
    
    def _get_effective_tools_config(self) -> Optional[Union[List[Dict[str, Any]], List, str]]:
        """Get effective tools configuration from instance configuration or recent chat.completions.create() call.
        
        This method provides automatic fallback to tools used in the most recent chat.completions.create() call,
        enabling seamless tool calling workflow where users can call tools directly after using them in chat completions.
        
        Priority order:
        1. Instance-level tools configuration (set via configure_tools())
        2. Tools from most recent chat.completions.create() call (cached automatically)
        
        Returns:
            Tools configuration from instance, recent chat call, or None if not configured
        """
        # First priority: explicitly configured tools via configure_tools()
        if self._tools_config is not None:
            return self._tools_config
            
        # Second priority: tools from most recent chat.completions.create() call
        # This enables the workflow: chat.completions.create(tools=...) -> client.call(tool_name, args)
        if hasattr(self, '_last_chat_tools_config') and self._last_chat_tools_config is not None:
            return self._last_chat_tools_config
            
        return None
    
    def _convert_tools_parameter(
        self,
        tools: Optional[Union[List[Dict[str, Any]], List, str]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Convenience method to access ChatCompletions tool conversion.
        
        Args:
            tools: Tools in various formats
            
        Returns:
            List of OpenAI-compatible tool definitions or None
        """
        return self.chat.completions._convert_tools_parameter(tools)
        
    def call(self, tool_name: str, arguments: Union[Dict[str, Any], str, set], tools: Optional[Union[List[Dict[str, Any]], List, str]] = None) -> Any:
        """
        Directly call a tool by name with the given arguments.
        
        This method provides a convenient way to execute tools without having to
        manually use get_registry() and Fn objects. It supports:
        - Tools registered via @tools decorator
        - Built-in tools (code_interpreter, web_search)
        - MCP tools (if configured)
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool (dict, JSON string, or other)
            tools: Optional tools configuration to automatically configure before calling
            
        Returns:
            Result of the tool execution
            
        Raises:
            ValueError: If the tool is not found or arguments are invalid
            ToolExecutionError: If the tool execution fails
        """
        # Automatically configure tools if provided
        if tools is not None:
            self.configure_tools(tools)
        
        # Import here to avoid circular imports
        from ..tools import get_registry
        from ..tools.builtin_tools import get_builtin_tool_class, is_builtin_tool
        from ..tools.mcp_manager import MCPManager
        
        # Enhanced argument processing with better error handling
        processed_args = self._process_arguments(arguments, tool_name)
        
        # First, try to get the tool from the main registry
        tool = get_registry().get_tool(tool_name)
        if tool:
            result = tool.call(processed_args)
            return result
        
        # If not found, check if it's a built-in tool
        if is_builtin_tool(tool_name):
            builtin_class = get_builtin_tool_class(tool_name)
            if builtin_class:
                # Create an instance of the built-in tool
                builtin_tool = builtin_class()
                # Convert it to an Fn object and call it
                fn_tool = builtin_tool.to_fn()
                result = fn_tool.call(processed_args)
                return result
        
        # If not found, check if it's an MCP tool using effective configuration
        # MCP tools are named with pattern: {server_name}-{tool_name}
        effective_tools_config = self._get_effective_tools_config()
        if effective_tools_config:
            try:
                # Initialize MCP manager with effective configuration if needed
                if not self._mcp_manager:
                    self._mcp_manager = self._get_mcp_manager_for_tools(effective_tools_config)
                
                if self._mcp_manager and self._mcp_manager.clients:
                    # Check if any MCP client has this tool
                    for client_id, client in self._mcp_manager.clients.items():
                        if hasattr(client, 'tools'):
                            for mcp_tool in client.tools:
                                # Extract server name from client_id (format: {server_name}_{uuid})
                                server_name = client_id.split('_')[0]
                                expected_tool_name = f"{server_name}-{mcp_tool.name}"
                                
                                if expected_tool_name == tool_name:
                                    # Found the MCP tool, create an Fn and call it
                                    fn_tool = self._mcp_manager._create_mcp_tool_fn(
                                        name=tool_name,
                                        client_id=client_id,
                                        mcp_tool_name=mcp_tool.name,
                                        description=mcp_tool.description if hasattr(mcp_tool, 'description') else f"MCP tool: {tool_name}",
                                        parameters=mcp_tool.inputSchema if hasattr(mcp_tool, 'inputSchema') else {'type': 'object', 'properties': {}, 'required': []}
                                    )
                                    result = fn_tool.call(processed_args)
                                    return result
            except ImportError:
                # MCP package not available, skip MCP tool checking
                pass
        
        # If still not found, provide a helpful error message with guidance
        error_msg = f"Tool '{tool_name}' not found"
        
        # Check if this looks like an MCP tool name pattern
        if '-' in tool_name and effective_tools_config:
            error_msg += f". Tool '{tool_name}' appears to be an MCP tool but MCP servers may not be properly initialized. Check that the MCP server is running and accessible."
        elif '-' in tool_name and not effective_tools_config:
            error_msg += f". Tool '{tool_name}' appears to be an MCP tool but no tools are configured."
        elif not effective_tools_config:
            error_msg += ". No tools are currently configured."
        else:
            error_msg += " in registry, built-in tools, or configured MCP tools"
        
        # Add helpful guidance based on the situation
        if not effective_tools_config:
            error_msg += "\n\nTo use tools with client.call(), you have two options:"
            error_msg += "\n1. First call chat.completions.create() with tools, then call client.call():"
            error_msg += "\n   response = client.chat.completions.create(model='gpt-4', messages=[...], tools=[...])"
            error_msg += "\n   result = client.call('tool_name', {'arg': 'value'})"
            error_msg += "\n2. Configure tools directly on the client:"
            error_msg += "\n   client.configure_tools([...])  # Then use client.call()"
            
        raise ValueError(error_msg)
    
    def _get_mcp_manager_for_tools(self, tools_config: Optional[Union[List[Dict[str, Any]], List, str]] = None) -> Optional[Any]:
        """Get or create MCP manager using specified or cached tools configuration.
        
        Args:
            tools_config: Optional tools configuration to use. If None, uses effective config.
        
        Returns:
            MCPManager instance with tools configured, or None if no MCP config found
        """
        if tools_config is None:
            tools_config = self._get_effective_tools_config()
            
        if not tools_config:
            return None
            
        try:
            from ..tools.mcp_manager import MCPManager
            
            # Find MCP server configs in the tools configuration
            mcp_configs = []
            if isinstance(tools_config, list):
                for item in tools_config:
                    if isinstance(item, dict) and "mcpServers" in item:
                        mcp_configs.append(item)
            
            if not mcp_configs:
                return None
            
            # Initialize MCP manager with the found configurations
            manager = MCPManager()
            
            # Initialize each MCP config (this populates manager.clients)
            for config in mcp_configs:
                try:
                    manager.init_config(config)  # This returns tools but also populates clients
                except Exception as e:
                    # If initialization fails, continue with other configs
                    print(f"Warning: Failed to initialize MCP config {config}: {e}")
                    continue
            
            return manager if manager.clients else None
            
        except ImportError:
            return None
    
    def _process_arguments(self, arguments: Union[Dict[str, Any], str, set], tool_name: str) -> Dict[str, Any]:
        """
        Process and validate arguments for tool execution.
        
        This method handles common user mistakes like:
        - Passing a set instead of a dict (from {json_string} syntax)
        - Passing a JSON string that needs parsing
        - Other argument format issues
        
        Args:
            arguments: Raw arguments in various formats
            tool_name: Name of the tool (for error messages)
            
        Returns:
            Processed arguments as a dictionary
            
        Raises:
            ValueError: If arguments cannot be processed
        """
        # Handle None or empty arguments
        if arguments is None:
            return {}
        
        # If it's already a dict, return as-is
        if isinstance(arguments, dict):
            return arguments
        
        # Handle common mistake: user used {json_string} which creates a set
        if isinstance(arguments, set):
            if len(arguments) == 1:
                # Try to extract and parse the single item
                json_str = next(iter(arguments))
                if isinstance(json_str, str):
                    try:
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict):
                            print(f"⚠️  Note: Detected set argument for '{tool_name}'. Use 'json.loads(tool_call.function.arguments)' instead of '{{tool_call.function.arguments}}'")
                            return parsed
                    except json.JSONDecodeError:
                        pass
            
            raise ValueError(
                f"Invalid arguments for tool '{tool_name}': received a set {arguments}. "
                f"Common mistake: use 'json.loads(tool_call.function.arguments)' instead of '{{tool_call.function.arguments}}'"
            )
        
        # Handle JSON string
        if isinstance(arguments, str):
            try:
                parsed = json.loads(arguments)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    raise ValueError(f"Invalid arguments for tool '{tool_name}': JSON string must parse to a dictionary, got {type(parsed)}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON arguments for tool '{tool_name}': {e}")
        
        # Handle other types
        raise ValueError(
            f"Invalid arguments for tool '{tool_name}': expected dict, JSON string, but got {type(arguments)}. "
            f"Received: {arguments}"
        )