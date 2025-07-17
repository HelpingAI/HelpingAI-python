"""Core classes and decorators for HelpingAI tool utilities."""

import json
import inspect
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, Union, List

from ..base_models import BaseModel
from .schema import generate_schema_from_function, validate_schema
from .errors import ToolExecutionError, SchemaValidationError, ToolRegistrationError


@dataclass
class Fn(BaseModel):
    """Represents a callable function/tool with metadata and standard tool format compatibility."""
    
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = None
    
    def to_tool_format(self) -> Dict[str, Any]:
        """Convert to standard tool format.
        
        Returns:
            Dict in format: {
                "type": "function",
                "function": {
                    "name": str,
                    "description": str,
                    "parameters": Dict[str, Any]
                }
            }
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def call(self, arguments: Union[str, Dict[str, Any]]) -> Any:
        """Execute the function with given arguments.
        
        Args:
            arguments: JSON string or dict of function arguments
            
        Returns:
            Function result
            
        Raises:
            ToolExecutionError: If function execution fails
            ValueError: If arguments are invalid
        """
        if not self.function:
            raise ToolExecutionError(
                f"No callable function provided for tool '{self.name}'",
                tool_name=self.name
            )
        
        if isinstance(arguments, str):
            try:
                args_dict = json.loads(arguments)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON arguments for tool '{self.name}': {e}")
        else:
            args_dict = arguments or {}
        
        try:
            # Validate arguments against schema
            self._validate_arguments(args_dict)
            return self.function(**args_dict)
        except Exception as e:
            if isinstance(e, (ValueError, TypeError)) and "argument" in str(e).lower():
                # Function signature mismatch
                raise ToolExecutionError(
                    f"Invalid arguments for tool '{self.name}': {e}",
                    tool_name=self.name,
                    original_error=e
                )
            else:
                # Function execution error
                raise ToolExecutionError(
                    f"Error executing tool '{self.name}': {e}",
                    tool_name=self.name,
                    original_error=e
                )
    
    def _validate_arguments(self, args: Dict[str, Any]) -> None:
        """Validate arguments against the parameter schema.
        
        Args:
            args: Arguments to validate
            
        Raises:
            SchemaValidationError: If validation fails
        """
        # Basic validation - check required parameters
        required_params = self.parameters.get("required", [])
        for param in required_params:
            if param not in args:
                raise SchemaValidationError(
                    f"Missing required parameter '{param}' for tool '{self.name}'",
                    schema=self.parameters,
                    value=args
                )
        
        # Check for unknown parameters
        allowed_params = set(self.parameters.get("properties", {}).keys())
        provided_params = set(args.keys())
        unknown_params = provided_params - allowed_params
        
        if unknown_params:
            raise SchemaValidationError(
                f"Unknown parameters for tool '{self.name}': {', '.join(unknown_params)}",
                schema=self.parameters,
                value=args
            )
    
    @classmethod
    def from_function(cls, func: Callable) -> 'Fn':
        """Create Fn from a function with automatic schema generation.
        
        Args:
            func: The callable function
            
        Returns:
            Fn instance with auto-generated schema
        """
        name = func.__name__
        desc = func.__doc__.strip() if func.__doc__ else f"Execute {name}"
        schema = generate_schema_from_function(func)
        
        return cls(
            name=name,
            description=desc,
            parameters=schema,
            function=func
        )


def tools(func: Callable = None) -> Union[Callable, Callable[[Callable], Callable]]:
    """Decorator to mark functions as callable tools.
    
    Can be used with or without parentheses:
    
    @tools
    def my_function():
        '''Function description from docstring'''
        pass
        
    Returns:
        Decorated function with tool metadata attached
    """
    def decorator(f: Callable) -> Callable:
        try:
            # Create Fn object from function using docstring
            fn_obj = Fn.from_function(f)
            
            # Register in global registry
            _get_global_registry().register(fn_obj)
            
            # Attach metadata to function
            f._hai_tool = fn_obj
            
            return f
            
        except Exception as e:
            raise ToolRegistrationError(
                f"Failed to register tool '{f.__name__}': {e}",
                tool_name=f.__name__
            ) from e
    
    # Handle both @tools and @tools() usage
    if func is None:
        # Called as @tools()
        return decorator
    else:
        # Called as @tools
        return decorator(func)


# Convenience functions for accessing tools
def get_tools(names: List[str] = None) -> List[Fn]:
    """Get registered tools.
    
    Args:
        names: Specific tool names to retrieve
        
    Returns:
        List of Fn objects
    """
    return _get_global_registry().get_tools(names)


def get_tools_format(names: List[str] = None) -> List[Dict[str, Any]]:
    """Get tools in standard tool format.
    
    Args:
        names: Specific tool names to retrieve
        
    Returns:
        List of tool definitions in standard format
    """
    tools_list = get_tools(names)
    return [tool.to_tool_format() for tool in tools_list]


def clear_registry():
    """Clear all registered tools (mainly for testing)."""
    _get_global_registry().clear()


def get_registry():
    """Get the global tool registry."""
    return _get_global_registry()


# Global registry management - will import from registry module
def _get_global_registry():
    """Get or create the global tool registry."""
    from .registry import _get_global_registry as _get_registry
    return _get_registry()