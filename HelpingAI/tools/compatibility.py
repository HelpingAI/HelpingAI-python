"""Compatibility utilities for seamless integration with existing code."""

from typing import List, Dict, Any, Union, Optional, TYPE_CHECKING

from .core import Fn
from .errors import ToolExecutionError

if TYPE_CHECKING:
    from .core import ToolDefinition


def convert_legacy_tools(tools: List[Dict[str, Any]]) -> List[Fn]:
    """Convert legacy tool format to Fn objects.
    
    Args:
        tools: List of tools in standard tool format
        
    Returns:
        List of Fn objects (without callable functions)
        
    Example:
        legacy_tools = [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather info",
                "parameters": {...}
            }
        }]
        fn_objects = convert_legacy_tools(legacy_tools)
    """
    fn_objects = []
    for tool in tools:
        if tool.get("type") == "function":
            func_def = tool["function"]
            fn_obj = Fn(
                name=func_def["name"],
                description=func_def["description"],
                parameters=func_def["parameters"],
                function=None  # No callable - just metadata
            )
            fn_objects.append(fn_obj)
    return fn_objects


def ensure_tool_format(
    tools: Union[List[Dict[str, Any]], List[Fn], str, None]
) -> Optional[List[Dict[str, Any]]]:
    """Ensure tools are in standard tool format regardless of input type.
    
    This is the core compatibility function used by ChatCompletions.create()
    
    Args:
        tools: Tools in various formats:
            - None: No tools
            - str: Category name to get from registry
            - List[Dict]: Already in standard format
            - List[Fn]: Fn objects to convert
            
    Returns:
        List of tool definitions in standard format or None
        
    Raises:
        ValueError: If tools format is not supported
    """
    if tools is None:
        return None
    
    if isinstance(tools, str):
        # Category name - get from registry
        from .core import get_tools_format
        return get_tools_format(category=tools)
    
    if isinstance(tools, list):
        if not tools:
            return []
        
        first_item = tools[0]
        
        # Already in standard format
        if isinstance(first_item, dict) and "type" in first_item:
            return tools
        
        # List of Fn objects
        if hasattr(first_item, 'to_tool_format'):
            return [tool.to_tool_format() for tool in tools]
    
    raise ValueError(f"Unsupported tools format: {type(tools)}. "
                    f"Expected None, str, List[Dict], or List[Fn].")


def validate_tool_compatibility(tools: Any) -> bool:
    """Validate that tools parameter is in a supported format.
    
    Args:
        tools: Tools parameter to validate
        
    Returns:
        True if format is supported, False otherwise
    """
    if tools is None:
        return True
    
    if isinstance(tools, str):
        return True  # Category name
    
    if isinstance(tools, list):
        if not tools:
            return True
        
        first_item = tools[0]
        
        # Standard tool format
        if isinstance(first_item, dict):
            return "type" in first_item and "function" in first_item
        
        # Fn objects
        if hasattr(first_item, 'to_tool_format'):
            return True
    
    return False


def get_compatibility_warnings(tools: Any) -> List[str]:
    """Get any compatibility warnings for the tools format.
    
    Args:
        tools: Tools parameter to check
        
    Returns:
        List of warning messages (empty if no issues)
    """
    warnings = []
    
    # Check for common migration opportunities
    if isinstance(tools, list) and tools:
        first_item = tools[0]
        if isinstance(first_item, dict) and "type" in first_item:
            warnings.append(
                "Consider using @tools decorator for easier tool definition. "
                "See documentation for migration examples."
            )
    
    return warnings


def merge_tool_lists(*tool_lists: Union[List[Dict[str, Any]], List[Fn], str, None]) -> List[Dict[str, Any]]:
    """Merge multiple tool lists of different formats into standard tool format.
    
    Args:
        *tool_lists: Variable number of tool lists in different formats
        
    Returns:
        Combined list of tools in standard format
        
    Example:
        # Combine decorated tools with legacy tools
        combined = merge_tool_lists(
            get_tools(category="weather"),  # Fn objects
            legacy_tools,                   # Standard format dicts
            "math"                         # Category name
        )
    """
    combined = []
    
    for tool_list in tool_lists:
        if tool_list is None:
            continue
            
        formatted_tools = ensure_tool_format(tool_list)
        if formatted_tools:
            combined.extend(formatted_tools)
    
    return combined


def create_fn_from_tool_dict(tool_dict: Dict[str, Any], function: callable = None) -> Fn:
    """Create an Fn object from a standard tool definition.
    
    Args:
        tool_dict: Standard tool definition
        function: Optional callable function to attach
        
    Returns:
        Fn object
        
    Raises:
        ValueError: If tool_dict is not in valid tool format
    """
    if not isinstance(tool_dict, dict) or tool_dict.get("type") != "function":
        raise ValueError("tool_dict must be a valid tool definition")
    
    func_def = tool_dict.get("function", {})
    
    return Fn(
        name=func_def.get("name", ""),
        description=func_def.get("description", ""),
        parameters=func_def.get("parameters", {}),
        function=function
    )


def is_tool_format(obj: Any) -> bool:
    """Check if an object is in standard tool format.
    
    Args:
        obj: Object to check
        
    Returns:
        True if object is in standard tool format
    """
    return (
        isinstance(obj, dict) and
        obj.get("type") == "function" and
        "function" in obj and
        isinstance(obj["function"], dict) and
        "name" in obj["function"] and
        "description" in obj["function"]
    )


def is_fn_object(obj: Any) -> bool:
    """Check if an object is an Fn instance.
    
    Args:
        obj: Object to check
        
    Returns:
        True if object is an Fn instance
    """
    return hasattr(obj, 'to_tool_format') and hasattr(obj, 'call')


def normalize_tool_choice(
    tool_choice: Union[str, Dict[str, Any], None],
    available_tools: List[Dict[str, Any]]
) -> Union[str, Dict[str, Any], None]:
    """Normalize tool_choice parameter for compatibility.
    
    Args:
        tool_choice: Original tool choice parameter
        available_tools: List of available tools
        
    Returns:
        Normalized tool choice parameter
    """
    if tool_choice is None:
        return None
    
    if isinstance(tool_choice, str):
        if tool_choice in ["auto", "none"]:
            return tool_choice
        
        # Check if it's a tool name
        tool_names = [tool["function"]["name"] for tool in available_tools]
        if tool_choice in tool_names:
            return {
                "type": "function",
                "function": {"name": tool_choice}
            }
    
    if isinstance(tool_choice, dict):
        return tool_choice
    
    # Default to auto for unsupported formats
    return "auto"


class ToolCompatibilityHelper:
    """Helper class for managing tool compatibility across different formats."""
    
    def __init__(self):
        self._conversion_cache = {}
    
    def convert_and_cache(self, tools: Any) -> List[Dict[str, Any]]:
        """Convert tools to standard tool format with caching.
        
        Args:
            tools: Tools in any supported format
            
        Returns:
            List of tool definitions in standard format
        """
        # Create cache key
        cache_key = self._create_cache_key(tools)
        
        if cache_key in self._conversion_cache:
            return self._conversion_cache[cache_key]
        
        # Convert and cache
        result = ensure_tool_format(tools)
        if result is not None:
            self._conversion_cache[cache_key] = result
        
        return result
    
    def _create_cache_key(self, tools: Any) -> str:
        """Create a cache key for tools."""
        if tools is None:
            return "none"
        
        if isinstance(tools, str):
            return f"category:{tools}"
        
        if isinstance(tools, list):
            if not tools:
                return "empty_list"
            
            # Create key based on tool names and types
            if hasattr(tools[0], 'name'):
                # Fn objects
                names = [tool.name for tool in tools]
                return f"fn_objects:{','.join(sorted(names))}"
            elif isinstance(tools[0], dict):
                # Standard tool format
                names = [tool.get("function", {}).get("name", "") for tool in tools]
                return f"tool_format:{','.join(sorted(names))}"
        
        return f"unknown:{type(tools).__name__}"
    
    def clear_cache(self):
        """Clear the conversion cache."""
        self._conversion_cache.clear()


# Global compatibility helper instance
_compatibility_helper = ToolCompatibilityHelper()


def get_compatibility_helper() -> ToolCompatibilityHelper:
    """Get the global compatibility helper instance."""
    return _compatibility_helper


def _convert_fns_to_tools(fns: Optional[List[Fn]]) -> List[Dict[str, Any]]:
    """Convert Fn objects to OpenAI tool format.
    
    Args:
        fns: List of Fn objects
        
    Returns:
        List of tool definitions in OpenAI format
    """
    if not fns:
        return []
    
    tools: List[Dict[str, Any]] = []
    for fn in fns:
        tool: Dict[str, Any] = {
            "type": "function",
            "function": {
                "name": fn.name,
                "description": fn.description,
                "parameters": fn.parameters  # fn.parameters is already a JSON schema object
            }
        }
        tools.append(tool)
    return tools


def ensure_openai_format(tools: Optional[Union[List[Dict[str, Any]], List[Fn], str]]) -> Optional[List[Dict[str, Any]]]:
    """Ensure tools are in OpenAI format regardless of input type.
    
    This function handles the conversion from various tool formats to the exact
    OpenAI tool calling format.
    
    Args:
        tools: Tools in various formats:
            - None: No tools
            - str: Category name to get from registry
            - List[Dict]: Already in OpenAI format
            - List[Fn]: Fn objects to convert
            
    Returns:
        List of tool definitions in OpenAI format or None
        
    Raises:
        ValueError: If tools format is not supported
    """
    if tools is None:
        return None
    
    if isinstance(tools, str):
        # Category name - get from registry
        from .core import get_tools
        fn_tools = get_tools(names=[tools] if tools else None)
        return _convert_fns_to_tools(fn_tools)
    
    if isinstance(tools, list):
        if not tools:
            return []
        
        first_item = tools[0]
        
        # Already in OpenAI format
        if isinstance(first_item, dict) and "type" in first_item:
            return tools
        
        # List of Fn objects
        if hasattr(first_item, 'to_tool_format'):
            return _convert_fns_to_tools(tools)
    
    raise ValueError(f"Unsupported tools format: {type(tools)}. "
                    f"Expected None, str, List[Dict], or List[Fn].")