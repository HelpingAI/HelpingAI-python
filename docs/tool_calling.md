# Tool Calling with HelpingAI

This guide explains how to use the HelpingAI tool calling framework to create and use AI-callable functions.

## Overview

The HelpingAI tool calling framework allows you to create functions that can be called by AI models. This is useful for:

- Retrieving real-time information
- Performing calculations
- Interacting with external APIs
- Executing custom business logic
- Creating multi-step workflows

## Creating Tools

### Method 1: Using the `@tools` Decorator (Recommended)

The easiest way to create a tool is to use the `@tools` decorator:

```python
from HelpingAI.tools import tools

@tools
def get_weather(city: str, units: str = "celsius") -> dict:
    """Get current weather information for a city.
    
    Args:
        city: The city name to get weather for
        units: Temperature units (celsius or fahrenheit)
    """
    # Your implementation here
    return {"temperature": 22, "units": units, "city": city}
```

The `@tools` decorator automatically:
- Generates JSON schema from Python type hints
- Extracts parameter descriptions from docstrings
- Registers the tool in the global registry
- Validates parameters against the schema

### Method 2: Using the `Fn` Class Directly

For more advanced use cases, you can create tools using the `Fn` class directly:

```python
from HelpingAI.tools import Fn, get_registry

calculator_tool = Fn(
    name="calculate",
    description="Perform a simple calculation",
    parameters={
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "The operation to perform",
                "enum": ["add", "subtract", "multiply", "divide"]
            },
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"}
        },
        "required": ["operation", "a", "b"]
    },
    function=lambda operation, a, b: {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero"
    }[operation]
)

# Register the tool manually
get_registry().register(calculator_tool)
```

## Using Tools with Chat Completions

Once you've created your tools, you can use them with chat completions:

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools

hai = HAI()
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=get_tools(),  # Include all registered tools
    tool_choice="auto"  # Let the model decide when to use tools
)
```

## Handling Tool Calls

When the model decides to use a tool, you need to handle the tool call:

```python
import json
from HelpingAI.tools import get_registry

if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    # Get the tool from registry
    tool = get_registry().get_tool(function_name)
    
    # Execute the tool
    result = tool.call(function_args)
    
    # Continue the conversation with the tool result
    follow_up = hai.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "user", "content": "What's the weather in Paris?"},
            response.choices[0].message,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result)
            }
        ]
    )
    
    print(follow_up.choices[0].message.content)
```

## Advanced Features

### Type System Support

The `@tools` decorator supports various Python type hints:

```python
from typing import List, Optional, Union, Literal
from enum import Enum

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@tools
def create_task(
    title: str,
    description: Optional[str] = None,
    priority: Priority = Priority.MEDIUM,
    tags: List[str] = None,
    due_date: Union[str, None] = None,
    status: Literal["todo", "in_progress", "done"] = "todo"
) -> dict:
    """Create a new task."""
    # Implementation
    return {"title": title, "status": "created"}
```

### Tool Registry Management

The tool registry provides methods for managing tools:

```python
from HelpingAI.tools import get_registry, get_tools, clear_registry

# Get the registry
registry = get_registry()

# List all tool names
tool_names = registry.list_tool_names()
print(f"Available tools: {tool_names}")

# Get a specific tool
weather_tool = registry.get_tool("get_weather")

# Check if a tool exists
if registry.has_tool("get_weather"):
    print("Weather tool is available")

# Get the total number of tools
tool_count = registry.size()
print(f"Total tools: {tool_count}")

# Get specific tools by name
weather_tools = get_tools(["get_weather", "get_forecast"])

# Clear all tools (mainly for testing)
clear_registry()
```

### Combining with Legacy Tools

You can combine your tools with existing OpenAI-format tools:

```python
from HelpingAI.tools import merge_tool_lists, get_tools

# Existing OpenAI-format tools
legacy_tools = [{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}]

# Combine with your tools
combined_tools = merge_tool_lists(
    legacy_tools,
    get_tools()
)

# Use in chat completion
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Help me with this"}],
    tools=combined_tools
)
```

### Error Handling

Handle errors that might occur during tool execution:

```python
from HelpingAI.tools import ToolExecutionError, SchemaValidationError

try:
    result = tool.call(arguments)
except SchemaValidationError as e:
    print(f"Invalid arguments: {e}")
    # Handle invalid arguments
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
    # Handle execution failure
```

## Best Practices

1. **Keep tools focused**: Each tool should do one thing well
2. **Provide clear descriptions**: Make sure your tool and parameter descriptions are clear
3. **Handle errors gracefully**: Implement proper error handling
4. **Use appropriate types**: Use the right type hints for your parameters
5. **Test your tools**: Make sure your tools work as expected before using them with AI
6. **Consider security**: Be careful about what your tools can do
7. **Use docstrings**: Provide detailed docstrings for your tools and parameters

## Example: Multi-turn Conversation with Tools

```python
import json
from HelpingAI import HAI
from HelpingAI.tools import tools, get_tools, get_registry

@tools
def get_weather(city: str) -> dict:
    """Get weather information for a city."""
    return {"temperature": 22, "city": city}

@tools
def get_time(timezone: str = "UTC") -> dict:
    """Get current time in a timezone."""
    import datetime
    return {"time": datetime.datetime.now().isoformat(), "timezone": timezone}

# Initialize client
hai = HAI()

# Start conversation
messages = [
    {"role": "system", "content": "You are a helpful assistant with access to tools."},
    {"role": "user", "content": "What's the weather in Paris and what time is it there?"}
]

# First turn
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=get_tools(),
    tool_choice="auto"
)

# Add assistant response to messages
messages.append(response.choices[0].message)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Execute the tool
        tool = get_registry().get_tool(function_name)
        result = tool.call(function_args)
        
        # Add tool response to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result)
        })

# Get final response
final_response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages
)

print(final_response.choices[0].message.content)
```