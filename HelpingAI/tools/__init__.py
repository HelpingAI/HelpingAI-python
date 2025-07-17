"""
HelpingAI Tools - Easy-to-use tool calling utilities.

This module provides decorators and utilities for creating standard
tool definitions from Python functions with minimal boilerplate.
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
    convert_legacy_tools,
    merge_tool_lists,
    create_fn_from_tool_dict,
    validate_tool_compatibility,
    get_compatibility_warnings
)

__version__ = "1.1.0"

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
    "convert_legacy_tools",
    "merge_tool_lists",
    "create_fn_from_tool_dict",
    "validate_tool_compatibility",
    "get_compatibility_warnings",
    
    # Error classes
    "ToolExecutionError",
    "SchemaValidationError",
    "ToolRegistrationError",
    "SchemaGenerationError",
]