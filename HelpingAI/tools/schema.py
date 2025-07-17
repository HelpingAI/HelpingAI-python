"""Schema generation utilities for HelpingAI tools."""

import inspect
import sys
from typing import get_type_hints, Union, Optional, List, Dict, Any, get_origin, get_args, Callable
from enum import Enum

from .errors import SchemaGenerationError


def generate_schema_from_function(func: Callable) -> Dict[str, Any]:
    """Generate OpenAI-compatible JSON schema from function signature.
    
    Args:
        func: Function to analyze
        
    Returns:
        JSON schema dict compatible with OpenAI tools format
        
    Raises:
        SchemaGenerationError: If schema generation fails
    """
    try:
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = type_hints.get(param_name, str)
            
            try:
                param_schema = _type_to_schema(param_type)
            except Exception as e:
                raise SchemaGenerationError(
                    f"Failed to generate schema for parameter '{param_name}' of type {param_type}",
                    function_name=func.__name__,
                    type_hint=param_type
                ) from e
            
            # Add description from docstring if available
            if func.__doc__:
                param_desc = _extract_param_description(func.__doc__, param_name)
                if param_desc:
                    param_schema['description'] = param_desc
            else:
                # Fallback description if no docstring
                param_schema['description'] = f"The {param_name} parameter"
            
            properties[param_name] = param_schema
            
            # Check if parameter is required (no default value and not Optional)
            is_optional = _is_optional_type(param_type)
            if param.default == inspect.Parameter.empty and not is_optional:
                required.append(param_name)
        
        schema = {
            "type": "object",
            "properties": properties
        }
        
        if required:
            schema["required"] = required
        
        return schema
        
    except Exception as e:
        if isinstance(e, SchemaGenerationError):
            raise
        raise SchemaGenerationError(
            f"Failed to generate schema for function '{func.__name__}': {str(e)}",
            function_name=func.__name__
        ) from e


def _is_optional_type(type_hint: Any) -> bool:
    """Check if a type hint represents an Optional type.
    
    Args:
        type_hint: Python type hint to check
        
    Returns:
        True if the type is Optional[T] (Union[T, None])
    """
    origin = get_origin(type_hint)
    args = get_args(type_hint)
    
    # Check if it's Union[T, None] (which is Optional[T])
    if origin is Union:
        return len(args) == 2 and type(None) in args
    
    return False


def _type_to_schema(type_hint: Any) -> Dict[str, Any]:
    """Convert Python type hint to JSON schema property.
    
    Args:
        type_hint: Python type hint
        
    Returns:
        JSON schema property definition
    """
    # Handle None type
    if type_hint is type(None):
        return {"type": "null"}
    
    # Get origin and args for generic types
    origin = get_origin(type_hint)
    args = get_args(type_hint)
    
    # Handle Union types (including Optional)
    if origin is Union:
        if len(args) == 2 and type(None) in args:
            # This is Optional[T] - just use the non-None type
            non_none_type = args[0] if args[1] is type(None) else args[1]
            return _type_to_schema(non_none_type)
        else:
            # Multiple types - use anyOf
            schemas = []
            for arg in args:
                if arg is not type(None):  # Skip None in unions
                    schemas.append(_type_to_schema(arg))
            
            if len(schemas) == 1:
                return schemas[0]
            return {"anyOf": schemas}
    
    # Handle List types
    if origin is list or origin is List:
        item_type = args[0] if args else str
        return {
            "type": "array",
            "items": _type_to_schema(item_type)
        }
    
    # Handle Dict types
    if origin is dict or origin is Dict:
        if len(args) >= 2:
            # Dict[str, T] - use additionalProperties
            value_type = args[1]
            return {
                "type": "object",
                "additionalProperties": _type_to_schema(value_type)
            }
        else:
            # Generic dict
            return {
                "type": "object",
                "additionalProperties": True
            }
    
    # Handle basic types with proper JSON schema type mapping
    if type_hint == str:
        return {"type": "string"}
    elif type_hint == int:
        return {"type": "integer"}
    elif type_hint == float:
        return {"type": "number"}
    elif type_hint == bool:
        return {"type": "boolean"}
    elif type_hint == bytes:
        return {"type": "string", "format": "byte"}
    
    # Handle Enum types
    if inspect.isclass(type_hint) and issubclass(type_hint, Enum):
        enum_values = [e.value for e in type_hint]
        # Determine the type of enum values
        if enum_values:
            first_value = enum_values[0]
            if isinstance(first_value, str):
                return {
                    "type": "string",
                    "enum": enum_values
                }
            elif isinstance(first_value, int):
                return {
                    "type": "integer",
                    "enum": enum_values
                }
            elif isinstance(first_value, float):
                return {
                    "type": "number",
                    "enum": enum_values
                }
        
        # Fallback for mixed or unknown enum types
        return {"enum": enum_values}
    
    # Handle typing.Literal (Python 3.8+)
    if hasattr(type_hint, '__origin__') and str(type_hint.__origin__) == 'typing.Literal':
        literal_values = list(args)
        if literal_values:
            first_value = literal_values[0]
            if isinstance(first_value, str):
                return {
                    "type": "string",
                    "enum": literal_values
                }
            elif isinstance(first_value, int):
                return {
                    "type": "integer",
                    "enum": literal_values
                }
            elif isinstance(first_value, float):
                return {
                    "type": "number",
                    "enum": literal_values
                }
        return {"enum": literal_values}
    
    # Handle custom classes - treat as objects
    if inspect.isclass(type_hint):
        return {
            "type": "object",
            "description": f"Object of type {type_hint.__name__}"
        }
    
    # Default to string for unknown types
    return {
        "type": "string",
        "description": f"Value of type {str(type_hint)}"
    }


def _extract_param_description(docstring: str, param_name: str) -> Optional[str]:
    """Extract parameter description from docstring.
    
    Supports multiple docstring formats:
    - Google style: Args: param_name: description
    - Sphinx style: :param param_name: description
    - NumPy style: Parameters section
    
    Args:
        docstring: Function docstring
        param_name: Parameter name to find
        
    Returns:
        Parameter description if found, None otherwise
    """
    if not docstring:
        return None
    
    lines = docstring.strip().split('\n')
    in_args_section = False
    in_params_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Google/standard style: Args: or Arguments:
        if line.lower().startswith('args:') or line.lower().startswith('arguments:'):
            in_args_section = True
            continue
        
        # NumPy style: Parameters
        if line.lower().startswith('parameters'):
            in_params_section = True
            continue
        
        # Exit sections on next section header
        if (in_args_section or in_params_section) and line.endswith(':') and not line.startswith(' '):
            in_args_section = False
            in_params_section = False
            continue
        
        # Sphinx style: :param param_name: description
        if line.startswith(f':param {param_name}:'):
            desc = line[len(f':param {param_name}:'):].strip()
            return desc if desc else None
        
        # Google style: param_name: description
        if in_args_section and line.startswith(param_name + ':'):
            desc = line[len(param_name) + 1:].strip()
            return desc if desc else None
        
        # NumPy style: param_name : type
        #     description
        if in_params_section and param_name in line and ':' in line:
            # Look for description on next line(s)
            desc_lines = []
            for j in range(i + 1, len(lines)):
                desc_line = lines[j].strip()
                if not desc_line or desc_line.endswith(':') or ':' in desc_line:
                    break
                desc_lines.append(desc_line)
            if desc_lines:
                return ' '.join(desc_lines)
    
    return None


def validate_schema(schema: Dict[str, Any]) -> bool:
    """Validate that a schema is properly formatted for OpenAI tools.
    
    Args:
        schema: Schema dictionary to validate
        
    Returns:
        True if schema is valid
        
    Raises:
        SchemaValidationError: If schema is invalid
    """
    from .errors import SchemaValidationError
    
    if not isinstance(schema, dict):
        raise SchemaValidationError("Schema must be a dictionary")
    
    if "type" not in schema:
        raise SchemaValidationError("Schema must have a 'type' field")
    
    if schema["type"] != "object":
        raise SchemaValidationError("Root schema type must be 'object'")
    
    if "properties" not in schema:
        raise SchemaValidationError("Schema must have a 'properties' field")
    
    if not isinstance(schema["properties"], dict):
        raise SchemaValidationError("Schema 'properties' must be a dictionary")
    
    # Validate each property
    for prop_name, prop_schema in schema["properties"].items():
        if not isinstance(prop_schema, dict):
            raise SchemaValidationError(f"Property '{prop_name}' schema must be a dictionary")
        
        if "type" not in prop_schema and "enum" not in prop_schema and "anyOf" not in prop_schema:
            raise SchemaValidationError(f"Property '{prop_name}' must have 'type', 'enum', or 'anyOf'")
    
    return True