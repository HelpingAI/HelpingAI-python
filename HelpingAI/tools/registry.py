"""Tool registry for managing decorated tools."""

from threading import Lock
from typing import Dict, List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Fn

from .errors import ToolRegistrationError


class ToolRegistry:
    """Thread-safe global registry for managing decorated tools."""
    
    def __init__(self):
        self._tools: Dict[str, 'Fn'] = {}
        self._lock = Lock()
    
    def register(self, fn: 'Fn') -> None:
        """Register a tool function.
        
        Args:
            fn: Fn object to register
            
        Raises:
            ToolRegistrationError: If tool name already exists
        """
        with self._lock:
            if fn.name in self._tools:
                raise ToolRegistrationError(
                    f"Tool '{fn.name}' already registered. Tool names must be unique.",
                    tool_name=fn.name
                )
            
            self._tools[fn.name] = fn
    
    def unregister(self, name: str) -> None:
        """Unregister a tool by name.
        
        Args:
            name: Tool name to unregister
        """
        with self._lock:
            if name in self._tools:
                self._tools.pop(name)
    
    def get_tools(self, names: List[str] = None) -> List['Fn']:
        """Get registered tools with filtering.
        
        Args:
            names: Specific tool names to retrieve
            
        Returns:
            List of matching Fn objects
        """
        with self._lock:
            results = []
            
            if names:
                # Get specific tools by name
                for name in names:
                    if name in self._tools:
                        results.append(self._tools[name])
            else:
                # Get all tools
                results.extend(self._tools.values())
            
            return results
    
    def get_tool(self, name: str) -> Optional['Fn']:
        """Get a specific tool by name.
        
        Args:
            name: Tool name to retrieve
            
        Returns:
            Fn object if found, None otherwise
        """
        with self._lock:
            return self._tools.get(name)
    
    def list_tool_names(self) -> List[str]:
        """List all registered tool names.
        
        Returns:
            List of tool names
        """
        tools = self.get_tools()
        return [tool.name for tool in tools]
    
    def to_tool_format(self, names: List[str] = None) -> List[Dict[str, any]]:
        """Convert registered tools to standard tool format.
        
        Args:
            names: Specific tool names to retrieve
            
        Returns:
            List of tool definitions in standard format
        """
        tools = self.get_tools(names)
        return [tool.to_tool_format() for tool in tools]
    
    def clear(self) -> None:
        """Clear all registered tools (mainly for testing)."""
        with self._lock:
            self._tools.clear()
    
    def size(self) -> int:
        """Get the number of registered tools.
        
        Returns:
            Number of registered tools
        """
        with self._lock:
            return len(self._tools)
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered.
        
        Args:
            name: Tool name to check
            
        Returns:
            True if tool is registered, False otherwise
        """
        with self._lock:
            return name in self._tools
    
    def update_tool(self, fn: 'Fn') -> None:
        """Update an existing tool registration.
        
        Args:
            fn: Updated Fn object
            
        Raises:
            ToolRegistrationError: If tool doesn't exist
        """
        with self._lock:
            if fn.name not in self._tools:
                raise ToolRegistrationError(
                    f"Cannot update tool '{fn.name}' - not registered",
                    tool_name=fn.name
                )
            
            # Update tool
            self._tools[fn.name] = fn
    
    def get_stats(self) -> Dict[str, any]:
        """Get registry statistics.
        
        Returns:
            Dictionary with registry statistics
        """
        with self._lock:
            return {
                "total_tools": len(self._tools)
            }


# Global registry instance
_global_registry = None
_registry_lock = Lock()


def _get_global_registry() -> ToolRegistry:
    """Get or create the global tool registry.
    
    Returns:
        Global ToolRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        with _registry_lock:
            if _global_registry is None:
                _global_registry = ToolRegistry()
    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry (mainly for testing).
    
    This creates a new empty registry instance.
    """
    global _global_registry
    with _registry_lock:
        _global_registry = ToolRegistry()