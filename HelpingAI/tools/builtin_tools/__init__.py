"""
Built-in Tools for HelpingAI SDK

This module provides built-in tools inspired by the Qwen-Agent repository.
These tools can be used alongside MCP servers by specifying simple string identifiers.

Available built-in tools:
- code_interpreter: Python code execution sandbox
- web_search: Web search functionality 
- doc_parser: Document parsing capabilities
- image_gen: Image generation
- retrieval: Information retrieval
- storage: File storage operations

Usage:
    tools = [
        {'mcpServers': {...}},  # MCP servers
        'code_interpreter',     # Built-in tools
        'web_search'
    ]
"""

from .code_interpreter import CodeInterpreterTool
from .web_search import WebSearchTool
from .doc_parser import DocParserTool
from .image_gen import ImageGenTool
from .retrieval import RetrievalTool
from .storage import StorageTool

# Registry of built-in tools
BUILTIN_TOOLS_REGISTRY = {
    'code_interpreter': CodeInterpreterTool,
    'web_search': WebSearchTool,
    'doc_parser': DocParserTool,
    'image_gen': ImageGenTool,
    'retrieval': RetrievalTool,
    'storage': StorageTool,
}

def get_builtin_tool_class(tool_name: str):
    """Get the class for a built-in tool by name.
    
    Args:
        tool_name: Name of the built-in tool
        
    Returns:
        Tool class if found, None otherwise
    """
    return BUILTIN_TOOLS_REGISTRY.get(tool_name)

def get_available_builtin_tools():
    """Get list of available built-in tool names.
    
    Returns:
        List of available built-in tool names
    """
    return list(BUILTIN_TOOLS_REGISTRY.keys())

def is_builtin_tool(tool_name: str) -> bool:
    """Check if a tool name refers to a built-in tool.
    
    Args:
        tool_name: Tool name to check
        
    Returns:
        True if it's a built-in tool, False otherwise
    """
    return tool_name in BUILTIN_TOOLS_REGISTRY

__all__ = [
    'CodeInterpreterTool',
    'WebSearchTool', 
    'DocParserTool',
    'ImageGenTool',
    'RetrievalTool',
    'StorageTool',
    'BUILTIN_TOOLS_REGISTRY',
    'get_builtin_tool_class',
    'get_available_builtin_tools',
    'is_builtin_tool',
]