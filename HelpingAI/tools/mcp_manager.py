"""MCP (Model Context Protocol) manager for HelpingAI SDK.

This module provides the MCPManager class for managing MCP server connections
and converting MCP tools (Model Context Protocol) to HelpingAI-compatible format.
"""

import asyncio
import atexit
import json
import threading
import time
import uuid
from typing import Dict, List, Optional, Union, Any

from ..error import HAIError
from .core import Fn
from .errors import ToolExecutionError, ToolRegistrationError
from .mcp_client import MCPClient


class MCPManager:
    """Singleton manager for MCP server connections and tool registration."""
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MCPManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'clients'):  # Only initialize once
            try:
                import mcp  # noqa
            except ImportError as e:
                raise ImportError(
                    'Could not import mcp. Please install mcp with `pip install -U mcp`.'
                ) from e

            self.clients: Dict[str, MCPClient] = {}
            self.loop = asyncio.new_event_loop()
            self.loop_thread = threading.Thread(target=self._start_loop, daemon=True)
            self.loop_thread.start()

            # Process tracking for cleanup
            self.processes = []
            self._monkey_patch_mcp_process_creation()

    def _monkey_patch_mcp_process_creation(self):
        """Monkey patch MCP process creation for cleanup tracking."""
        try:
            import mcp.client.stdio
            target = mcp.client.stdio._create_platform_compatible_process
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(
                'MCP integration needs to monkey patch MCP for process cleanup. '
                'Please upgrade MCP to a higher version with `pip install -U mcp`.'
            ) from e

        async def _patched_create_process(*args, **kwargs):
            process = await target(*args, **kwargs)
            self.processes.append(process)
            return process

        mcp.client.stdio._create_platform_compatible_process = _patched_create_process

    def _start_loop(self):
        """Start the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)

        # Set exception handler for MCP SSE connection issues
        def exception_handler(loop, context):
            exception = context.get('exception')
            if exception:
                # Silently handle cross-task exceptions from MCP SSE connections
                if (isinstance(exception, RuntimeError) and
                        'Attempted to exit cancel scope in a different task' in str(exception)):
                    return
                if (isinstance(exception, BaseExceptionGroup) and
                        'Attempted to exit cancel scope in a different task' in str(exception)):
                    return

            # Handle other exceptions normally
            loop.default_exception_handler(context)

        self.loop.set_exception_handler(exception_handler)
        self.loop.run_forever()

    def is_valid_mcp_servers_config(self, config: Dict[str, Any]) -> bool:
        """Validate MCP servers configuration format.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid
            
        Example valid config:
        {
            "mcpServers": {
                "time": {
                    "command": "uvx",
                    "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
                },
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"]
                }
            }
        }
        """
        # Check if the top-level key "mcpServers" exists and is a dictionary
        if not isinstance(config, dict) or 'mcpServers' not in config:
            return False
        
        mcp_servers = config['mcpServers']
        if not isinstance(mcp_servers, dict):
            return False

        # Check each server configuration
        for server_name, server_config in mcp_servers.items():
            if not isinstance(server_config, dict):
                return False
            
            # Check for command-based configuration
            if 'command' in server_config:
                if not isinstance(server_config['command'], str):
                    return False
                if 'args' not in server_config or not isinstance(server_config['args'], list):
                    return False
            
            # Check for URL-based configuration
            if 'url' in server_config:
                if not isinstance(server_config['url'], str):
                    return False
                if 'headers' in server_config and not isinstance(server_config['headers'], dict):
                    return False
            
            # Environment variables must be a dictionary if present
            if 'env' in server_config and not isinstance(server_config['env'], dict):
                return False

        return True

    def init_config(self, config: Dict[str, Any]) -> List[Fn]:
        """Initialize MCP tools from server configuration.
        
        Args:
            config: MCP servers configuration
            
        Returns:
            List of Fn objects representing MCP tools
            
        Raises:
            ValueError: If configuration is invalid
            HAIError: If initialization fails
        """
        if not self.is_valid_mcp_servers_config(config):
            raise ValueError('Invalid MCP servers configuration')

        # Submit coroutine to event loop and wait for result
        future = asyncio.run_coroutine_threadsafe(
            self._init_config_async(config), 
            self.loop
        )
        
        try:
            return future.result()
        except Exception as e:
            raise HAIError(f'Failed to initialize MCP tools: {e}') from e

    async def _init_config_async(self, config: Dict[str, Any]) -> List[Fn]:
        """Async implementation of MCP configuration initialization."""
        tools: List[Fn] = []
        mcp_servers = config['mcpServers']
        
        for server_name, server_config in mcp_servers.items():
            client = MCPClient()
            
            # Connect to the MCP server
            await client.connect_server(server_name, server_config)
            
            # Generate unique client ID
            client_id = f"{server_name}_{uuid.uuid4()}"
            client.client_id = client_id
            self.clients[client_id] = client
            
            # Convert MCP tools to Fn objects
            for mcp_tool in client.tools:
                # Create tool parameters schema
                parameters = mcp_tool.inputSchema
                if 'required' not in parameters:
                    parameters['required'] = []
                
                # Ensure schema has required fields
                required_fields = {'type', 'properties', 'required'}
                missing_fields = required_fields - parameters.keys()
                if missing_fields:
                    raise ValueError(f'Missing required schema fields: {missing_fields}')

                # Clean up parameters to only include standard fields
                cleaned_parameters = {
                    'type': parameters['type'],
                    'properties': parameters['properties'],
                    'required': parameters['required']
                }
                
                # Create tool name and Fn object
                tool_name = f"{server_name}-{mcp_tool.name}"
                fn_obj = self._create_mcp_tool_fn(
                    name=tool_name,
                    client_id=client_id,
                    mcp_tool_name=mcp_tool.name,
                    description=mcp_tool.description,
                    parameters=cleaned_parameters
                )
                tools.append(fn_obj)

            # Add resource tools if available
            if client.resources:
                # List resources tool
                list_resources_name = f"{server_name}-list_resources"
                list_resources_fn = self._create_mcp_tool_fn(
                    name=list_resources_name,
                    client_id=client_id,
                    mcp_tool_name='list_resources',
                    description=(
                        'List available resources from the MCP server. '
                        'Resources represent data sources that can be used as context.'
                    ),
                    parameters={'type': 'object', 'properties': {}, 'required': []}
                )
                tools.append(list_resources_fn)

                # Read resource tool
                read_resource_name = f"{server_name}-read_resource"
                read_resource_fn = self._create_mcp_tool_fn(
                    name=read_resource_name,
                    client_id=client_id,
                    mcp_tool_name='read_resource',
                    description=(
                        'Read a specific resource by URI. '
                        'Use list_resources first to discover available URIs.'
                    ),
                    parameters={
                        'type': 'object',
                        'properties': {
                            'uri': {
                                'type': 'string',
                                'description': 'The URI of the resource to read'
                            }
                        },
                        'required': ['uri']
                    }
                )
                tools.append(read_resource_fn)

        return tools

    def _create_mcp_tool_fn(
        self, 
        name: str, 
        client_id: str, 
        mcp_tool_name: str, 
        description: str, 
        parameters: Dict[str, Any]
    ) -> Fn:
        """Create an Fn object for an MCP tool.
        
        Args:
            name: Tool name for registration
            client_id: MCP client identifier
            mcp_tool_name: Original MCP tool name
            description: Tool description
            parameters: Tool parameters schema
            
        Returns:
            Fn object that can execute the MCP tool
        """
        def mcp_tool_function(**kwargs) -> str:
            """Execute the MCP tool with given arguments."""
            # Get the MCP client
            if client_id not in self.clients:
                raise ToolExecutionError(
                    f"MCP client '{client_id}' not found",
                    tool_name=name
                )
            
            client = self.clients[client_id]
            
            # Execute the tool asynchronously
            future = asyncio.run_coroutine_threadsafe(
                client.execute_function(mcp_tool_name, kwargs),
                self.loop
            )
            
            try:
                return future.result()
            except Exception as e:
                raise ToolExecutionError(
                    f"Failed to execute MCP tool '{name}': {e}",
                    tool_name=name,
                    original_error=e
                )

        # Create Fn object
        return Fn(
            name=name,
            description=description,
            parameters=parameters,
            function=mcp_tool_function
        )

    def shutdown(self):
        """Shutdown the MCP manager and clean up resources."""
        futures = []
        
        # Clean up all clients
        for client_id in list(self.clients.keys()):
            client = self.clients[client_id]
            future = asyncio.run_coroutine_threadsafe(client.cleanup(), self.loop)
            futures.append(future)
            del self.clients[client_id]
        
        # Wait for graceful cleanup
        time.sleep(1)
        
        # Force terminate processes if needed
        if asyncio.all_tasks(self.loop):
            for process in self.processes:
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass  # Process may have already exited

        # Stop the event loop
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.loop_thread.join()


def _cleanup_mcp(_sig_num=None, _frame=None):
    """Cleanup function for MCP manager on exit."""
    if MCPManager._instance is None:
        return
    manager = MCPManager()
    manager.shutdown()


# Register cleanup function
if threading.current_thread() is threading.main_thread():
    atexit.register(_cleanup_mcp)