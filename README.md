# HelpingAI Python SDK

The official Python library for the [HelpingAI](https://helpingai.co) API - Advanced AI with Emotional Intelligence

[![PyPI version](https://badge.fury.io/py/helpingai.svg)](https://badge.fury.io/py/helpingai)
[![Python Versions](https://img.shields.io/pypi/pyversions/helpingai.svg)](https://pypi.org/project/helpingai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **OpenAI-Compatible API**: Drop-in replacement with familiar interface
- **Emotional Intelligence**: Advanced AI models with emotional understanding
- **MCP Integration**: Seamless connection to external tools via Multi-Channel Protocol servers
- **Tool Calling Made Easy**: [`@tools decorator`](HelpingAI/tools/core.py:144) for effortless function-to-tool conversion
- **Direct Tool Execution**: Simple `.call()` method for executing tools without registry manipulation
- **Automatic Schema Generation**: Type hint-based JSON schema creation with docstring parsing
- **Universal Tool Compatibility**: Seamless integration with OpenAI-format tools
- **Streaming Support**: Real-time response streaming
- **Comprehensive Error Handling**: Detailed error types and retry mechanisms
- **Type Safety**: Full type hints and IDE support
- **Flexible Configuration**: Environment variables and direct initialization

## 📦 Installation

```bash
pip install HelpingAI
```

### Optional Features

```bash
# Install with MCP (Multi-Channel Protocol) support
pip install HelpingAI[mcp]
```

## 🔑 Authentication

Get your API key from the [HelpingAI Dashboard](https://helpingai.co/dashboard).

### Environment Variable (Recommended)

```bash
export HAI_API_KEY='your-api-key'
```

### Direct Initialization

```python
from HelpingAI import HAI

hai = HAI(api_key='your-api-key')
```

## 🎯 Quick Start

```python
from HelpingAI import HAI

# Initialize client
hai = HAI()

# Create a chat completion
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "system", "content": "You are an expert in emotional intelligence."},
        {"role": "user", "content": "What makes a good leader?"}
    ]
)

print(response.choices[0].message.content)
```

## 🌊 Streaming Responses

```python
# Stream responses in real-time
for chunk in hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Tell me about empathy"}],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## ⚙️ Advanced Configuration

### Parameter Control

```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Write a story about empathy"}],
    temperature=0.7,        # Controls randomness (0-1)
    max_tokens=500,        # Maximum length of response
    top_p=0.9,            # Nucleus sampling parameter
    frequency_penalty=0.3, # Reduces repetition
    presence_penalty=0.3,  # Encourages new topics
    hide_think=True       # Filter out reasoning blocks
)
```

### Client Configuration

```python
hai = HAI(
    api_key="your-api-key",
    base_url="https://api.helpingai.co/v1",  # Custom base URL
    timeout=30.0,                            # Request timeout
    organization="your-org-id"               # Organization ID
)
```

## 🛡️ Error Handling

```python
from HelpingAI import HAI, HAIError, RateLimitError, InvalidRequestError
import time

def make_completion_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=messages
            )
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(e.retry_after or 1)
        except InvalidRequestError as e:
            print(f"Invalid request: {str(e)}")
            raise
        except HAIError as e:
            print(f"API error: {str(e)}")
            raise
```

## 🤖 Available Models

### Dhanishtha-2.0-preview
- **World's First Intermediate Thinking Model**: Multi-phase reasoning with self-correction capabilities
- **Unique Features**: `<think>...</think>` blocks for transparent reasoning, structured emotional reasoning (SER)
- **Best For**: Complex problem-solving, analytical tasks, educational content, reasoning-heavy applications

### Dhanishtha-2.0-preview-mini
- **Lightweight Reasoning Model**: Efficient version of Dhanishtha-2.0-preview
- **Unique Features**: Same reasoning capabilities in a more compact model
- **Best For**: Faster responses, mobile applications, resource-constrained environments

```python
# List all available models
models = hai.models.list()
for model in models:
    print(f"Model: {model.id} - {model.description}")

# Get specific model info
model = hai.models.retrieve("Dhanishtha-2.0-preview")
print(f"Model: {model.name}")

# Use Dhanishtha-2.0 for complex reasoning
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Solve this step by step: What's 15% of 240?"}],
    hide_think=False  # Show reasoning process
)
```
## 🛠️ MCP (Multi-Channel Protocol) Integration

Connect to external tools and services through MCP servers for expanded AI capabilities.

### Quick Start with MCP

```python
from HelpingAI import HAI

client = HAI(api_key="your-api-key")

# Configure MCP servers
tools = [
    {
        'mcpServers': {
            'time': {
                'command': 'uvx',
                'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
            },
            "fetch": {
                "command": "uvx",
                "args": ["mcp-server-fetch"]
            }
        }
    }
]

# Use MCP tools in chat completion
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What time is it in Shanghai?"}],
    tools=tools
)

print(response.choices[0].message.content)
```

### Supported Server Types

```python
# Stdio-based servers (most common)
{
    'command': 'uvx',
    'args': ['mcp-server-time'],
    'env': {'TIMEZONE': 'UTC'}  # optional
}

# HTTP SSE servers
{
    'url': 'https://api.example.com/mcp',
    'headers': {'Authorization': 'Bearer token'},
    'sse_read_timeout': 300
}

# Streamable HTTP servers
{
    'type': 'streamable-http',
    'url': 'http://localhost:8000/mcp'
}
```

### Popular MCP Servers

- **mcp-server-time** - Time and timezone operations
- **mcp-server-fetch** - HTTP requests and web scraping
- **mcp-server-filesystem** - File system operations
- **mcp-server-memory** - Persistent memory across conversations
- **mcp-server-sqlite** - SQLite database operations
- **Custom servers** - Any MCP-compliant server

### Combined Usage

Mix MCP servers with regular tools:

```python
# Regular OpenAI tools
regular_tools = [{
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Perform calculations",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            }
        }
    }
}]

# Combined with MCP servers
all_tools = regular_tools + [{
    'mcpServers': {
        'time': {
            'command': 'uvx',
            'args': ['mcp-server-time']
        }
    }
}]

response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Calculate 2+2 and tell me the current time"}],
    tools=all_tools
)
```

### Installation & Setup

```bash
# Install MCP support
pip install HelpingAI[mcp]

# Or install MCP package separately
pip install -U mcp
```

**Note**: MCP functionality requires the `mcp` package. The SDK provides graceful error handling when MCP is not installed.

## 🔧 Tool Calling with @tools Decorator

Transform any Python function into a powerful AI tool with zero boilerplate using the [`@tools`](HelpingAI/tools/core.py:144) decorator.

### Quick Start with Tools

```python
from HelpingAI import HAI
from HelpingAI.tools import tools, get_tools

@tools
def get_weather(city: str, units: str = "celsius") -> str:
    """Get current weather information for a city.
    
    Args:
        city: The city name to get weather for
        units: Temperature units (celsius or fahrenheit)
    """
    # Your weather API logic here
    return f"Weather in {city}: 22°{units[0].upper()}"

@tools
def calculate_tip(bill_amount: float, tip_percentage: float = 15.0) -> dict:
    """Calculate tip and total amount for a bill.
    
    Args:
        bill_amount: The original bill amount
        tip_percentage: Tip percentage (default: 15.0)
    """
    tip = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip
    return {"tip": tip, "total": total, "original": bill_amount}

# Use with chat completions
hai = HAI()
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's the weather in Paris and calculate tip for $50 bill?"}],
    tools=get_tools()  # Automatically includes all @tools functions
)

print(response.choices[0].message.content)
```

### Direct Tool Execution

The HAI client provides a convenient `.call()` method to directly execute tools without having to manually use the registry:

```python
from HelpingAI import HAI
from HelpingAI.tools import tools

@tools
def search(query: str, max_results: int = 5):
    """Search the web for information"""
    # Implementation here
    return {"results": [{"title": "Result 1", "url": "https://example.com"}]}

# Create a client instance
client = HAI()

# Directly call a tool by name with arguments
search_result = client.call("search", {"query": "python programming", "max_results": 3})
print("Search results:", search_result)

# You can also execute tools from model responses
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "search for quantum computing"}],
    tools=get_tools(),
    tool_choice="auto"
)

# Extract tool name and arguments from the model's tool call
tool_call = response.choices[0].message.tool_calls[0]
tool_name = tool_call.function.name
tool_args = json.loads(tool_call.function.arguments)

# Execute the tool directly
tool_result = client.call(tool_name, tool_args)
print(f"Result: {tool_result}")
```

### Advanced Tool Features

#### Type System Support
The [`@tools`](HelpingAI/tools/core.py:144) decorator automatically generates JSON schemas from Python type hints:

```python
from typing import List, Optional, Union
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
    due_date: Union[str, None] = None
) -> dict:
    """Create a new task with advanced type support.
    
    Args:
        title: Task title
        description: Optional task description
        priority: Task priority level
        tags: List of task tags
        due_date: Due date in YYYY-MM-DD format
    """
    return {
        "title": title,
        "description": description,
        "priority": priority.value,
        "tags": tags or [],
        "due_date": due_date
    }
```

#### Tool Registry Management

```python
from HelpingAI.tools import get_tools, get_registry, clear_registry

# Get specific tools
weather_tools = get_tools(["get_weather", "calculate_tip"])

# Registry inspection
registry = get_registry()
print(f"Registered tools: {registry.list_tool_names()}")
print(f"Total tools: {registry.size()}")

# Check if tool exists
if registry.has_tool("get_weather"):
    weather_tool = registry.get_tool("get_weather")
    print(f"Tool: {weather_tool.name} - {weather_tool.description}")
```

#### Universal Tool Compatibility

Seamlessly combine [`@tools`](HelpingAI/tools/core.py:144) functions with existing OpenAI-format tools:

```python
from HelpingAI.tools import merge_tool_lists, ensure_tool_format

# Existing OpenAI-format tools
legacy_tools = [{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    }
}]

# Combine with @tools functions
combined_tools = merge_tool_lists(
    legacy_tools,           # Existing tools
    get_tools(),            # @tools functions
    "math"                  # Category name (if you have categorized tools)
)

# Use in chat completion
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Help me with weather, calculations, and web search"}],
    tools=combined_tools
)
```

### Error Handling & Best Practices

```python
from HelpingAI.tools import ToolExecutionError, SchemaValidationError, ToolRegistrationError

@tools
def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers safely.
    
    Args:
        a: The dividend  
        b: The divisor
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# Handle tool execution in your application
def execute_tool_safely(tool_name: str, arguments: dict):
    try:
        # You can use the direct call method instead of registry manipulation
        hai = HAI()
        return hai.call(tool_name, arguments)
        
    except ToolExecutionError as e:
        print(f"Tool execution failed: {e}")
        return {"error": str(e)}
    except SchemaValidationError as e:
        print(f"Invalid arguments: {e}")
        return {"error": "Invalid parameters provided"}
    except ToolRegistrationError as e:
        print(f"Tool registration issue: {e}")
        return {"error": "Tool configuration error"}

# Example usage
result = execute_tool_safely("divide_numbers", {"a": 10, "b": 2})
print(result)  # 5.0

error_result = execute_tool_safely("divide_numbers", {"a": 10, "b": 0})
print(error_result)  # {"error": "Cannot divide by zero"}
```

### Migration from Legacy Tools

Transform your existing tool definitions with minimal effort:

**Before (Manual Schema):**
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather", 
        "description": "Get weather information",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "units": {"type": "string", "description": "Temperature units", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    }
}]
```

**After (@tools Decorator):**
```python
from typing import Literal

@tools
def get_weather(city: str, units: Literal["celsius", "fahrenheit"] = "celsius") -> str:
    """Get weather information
    
    Args:
        city: City name
        units: Temperature units
    """
    # Implementation here
    pass
```

The [`@tools`](HelpingAI/tools/core.py:144) decorator automatically:
- ✅ Generates JSON schema from type hints
- ✅ Extracts descriptions from docstrings  
- ✅ Handles required/optional parameters
- ✅ Supports multiple docstring formats (Google, Sphinx, NumPy)
- ✅ Provides comprehensive error handling
- ✅ Maintains thread-safe tool registry


## 📚 Documentation

Comprehensive documentation is available:

- [📖 Getting Started Guide](docs/getting_started.md) - Installation and basic usage
- [🔧 API Reference](docs/api_reference.md) - Complete API documentation
- [🛠️ Tool Calling Guide](docs/tool_calling.md) - Creating and using AI-callable tools
- [🔌 MCP Integration Guide](docs/mcp_integration.md) - Multi-Channel Protocol integration
- [💡 Examples](docs/examples.md) - Code examples and use cases
- [❓ FAQ](docs/faq.md) - Frequently asked questions


## 🔧 Requirements

- **Python**: 3.7-3.14
- **Dependencies**: 
  - `requests` - HTTP client
  - `typing_extensions` - Type hints support

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

- **Issues**: [GitHub Issues](https://github.com/HelpingAI/HelpingAI-python/issues)
- **Documentation**: [HelpingAI Docs](https://helpingai.co/docs)
- **Dashboard**: [HelpingAI Dashboard](https://helpingai.co/dashboard)
- **Email**: Team@helpingai.co


**Built with ❤️ by the HelpingAI Team**

*Empowering AI with Emotional Intelligence*