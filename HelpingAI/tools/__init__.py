"""

HelpingAI Tools - Easy-to-use tool calling utilities.

This module provides decorators and utilities for creating standard
tool definitions from Python functions with minimal boilerplate.

Key components:
- @tools decorator: Transform Python functions into AI-callable tools
- Fn class: Represent callable functions with metadata
- get_tools(): Get registered tools (preferred over get_tools_format)
- get_registry(): Access the tool registry for advanced management
- MCP integration: Support for Model Context Protocol servers
- Built-in tools: Pre-built tools inspired by Qwen-Agent (code_interpreter, web_search, etc.)
"""

from .core import Fn, tools, get_tools, get_tools_format, clear_registry, get_registry
from .registry import ToolRegistry
from .schema import generate_schema_from_function, validate_schema
from .errors import (
    ToolExecutionError,
    SchemaValidationError,
    ToolRegistrationError,
    SchemaGenerationError
)
from .compatibility import (
    ensure_tool_format,
    ensure_openai_format,
    convert_legacy_tools,
    merge_tool_lists,
    create_fn_from_tool_dict,
    validate_tool_compatibility,
    get_compatibility_warnings
)
from .builtin_tools import (
    get_builtin_tool_class,
    get_available_builtin_tools,
    is_builtin_tool,
    BUILTIN_TOOLS_REGISTRY
)
from .mcp_manager import MCPManager

__version__ = "1.1.3"

__all__ = [
    # Core classes and functions
    "Fn",
    "ToolRegistry",
    
    # Decorators and utilities
    "tools",
    "get_tools",
    "get_tools_format",
    "get_registry",
    "clear_registry",
    
    # Schema utilities
    "generate_schema_from_function",
    "validate_schema",
    
    # Compatibility utilities
    "ensure_tool_format",
    "ensure_openai_format",
    "convert_legacy_tools",
    "merge_tool_lists",
    "create_fn_from_tool_dict",
    "validate_tool_compatibility",
    "get_compatibility_warnings",
    
    # Built-in tools
    "get_builtin_tool_class",
    "get_available_builtin_tools", 
    "is_builtin_tool",
    "BUILTIN_TOOLS_REGISTRY",
    
    # MCP integration
    "MCPManager",
    
    # Error classes
    "ToolExecutionError",
    "SchemaValidationError",
    "ToolRegistrationError",
    "SchemaGenerationError",
]