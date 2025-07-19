# Built-in Tools for HelpingAI SDK

This document describes the built-in tools feature that allows you to use pre-built tools alongside MCP servers and custom tools.

## Overview

Built-in tools are ready-to-use tools inspired by the Qwen-Agent repository that can be specified using simple string identifiers. They integrate seamlessly with the existing MCP (Model Context Protocol) infrastructure and OpenAI-format tools.

## Available Built-in Tools

### 1. `code_interpreter`
**Execute Python code in a sandboxed environment**

- Supports common libraries (when available): numpy, pandas, matplotlib, seaborn
- Automatic plot saving for matplotlib figures
- Safe subprocess execution with timeout
- Handles both stdout and stderr output

```python
tools = ['code_interpreter']

# The AI can now execute Python code like:
# - Data analysis with pandas
# - Mathematical calculations
# - Creating visualizations with matplotlib
# - General Python programming tasks
```

### 2. `web_search`
**Search the web using DuckDuckGo**

- No API key required
- Returns formatted search results with titles, snippets, and URLs
- Configurable number of results
- Real-time web information access

```python
tools = ['web_search']

# The AI can search for:
# - Current events and news
# - Technical documentation
# - General information
# - Research topics
```

### 3. `doc_parser`
**Parse and extract text from documents**

- Currently supports text files
- Configurable text length limits
- Extensible for PDF, DOCX, and other formats
- URL and local file support

```python
tools = ['doc_parser']

# The AI can parse:
# - Text files
# - Documents from URLs
# - Extract content for analysis
```

### 4. `storage`
**File storage and management**

- Store, retrieve, list, and delete files
- Persistent storage across conversations
- Simple file management operations
- Secure file handling

```python
tools = ['storage']

# The AI can:
# - Store generated content
# - Retrieve previously saved files
# - Manage file collections
# - Organize data persistently
```

### 5. `image_gen`
**Image generation capabilities** (Placeholder)

- Ready for integration with AI image generation services
- Configurable image sizes and prompts
- Extensible for DALL-E, Stable Diffusion, etc.

### 6. `retrieval`
**Information retrieval and semantic search** (Placeholder)

- Ready for integration with vector databases
- Semantic search capabilities
- Document collections management
- Extensible for RAG applications

## Usage Examples

### Basic Usage
```python
from HelpingAI import HAI

client = HAI(api_key="your-api-key")

# Use built-in tools with simple string identifiers
tools = [
    'code_interpreter',
    'web_search',
    'storage'
]

response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[
        {"role": "user", "content": "Search for Python tutorials and create a learning plan"}
    ],
    tools=tools
)
```

### Mixed Configuration (The Requested Format)
```python
# Exact format requested by the user
tools = [
    {
        'mcpServers': {  # MCP server configurations
            'time': {
                'command': 'uvx',
                'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
            },
            "fetch": {
                "command": "uvx",
                "args": ["mcp-server-fetch"]
            }
        }
    },
    'code_interpreter',  # Built-in tools as simple strings
    'web_search',
    'doc_parser'
]

response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[
        {"role": "user", "content": "What time is it and can you search for AI news?"}
    ],
    tools=tools
)
```

### Advanced Mixed Configuration
```python
tools = [
    # MCP servers
    {
        'mcpServers': {
            'time': {'command': 'uvx', 'args': ['mcp-server-time']},
            'fetch': {'command': 'uvx', 'args': ['mcp-server-fetch']}
        }
    },
    # Built-in tools
    'code_interpreter',
    'web_search',
    'storage',
    # Custom OpenAI-format tool
    {
        "type": "function",
        "function": {
            "name": "custom_calculator",
            "description": "Custom calculation tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"]
            }
        }
    }
]
```

## Integration Details

### Compatibility Layer
The built-in tools integrate seamlessly with the existing compatibility layer:

```python
from HelpingAI.tools.compatibility import ensure_openai_format

# Handles mixed tool configurations automatically
tools = ['code_interpreter', 'web_search']
openai_format = ensure_openai_format(tools)
# Returns list of OpenAI-compatible tool definitions
```

### Registry System
```python
from HelpingAI.tools import (
    get_available_builtin_tools,
    is_builtin_tool,
    get_builtin_tool_class
)

# Get all available built-in tools
available = get_available_builtin_tools()
print(available)  # ['code_interpreter', 'web_search', ...]

# Check if a tool is built-in
if is_builtin_tool('code_interpreter'):
    tool_class = get_builtin_tool_class('code_interpreter')
```

### Direct Tool Usage
```python
# Use tools directly (for testing or advanced usage)
from HelpingAI.tools.builtin_tools.code_interpreter import CodeInterpreterTool

tool = CodeInterpreterTool()
result = tool.execute(code="print('Hello, World!')")
print(result)
```

## Error Handling

Built-in tools include comprehensive error handling:

```python
# Unknown tool names raise ValueError
try:
    tools = ['unknown_tool']
    ensure_openai_format(tools)
except ValueError as e:
    print(f"Error: {e}")  # "Unknown built-in tool: unknown_tool"

# Tool execution errors are wrapped in ToolExecutionError
from HelpingAI.tools.errors import ToolExecutionError
```

## Extension and Customization

### Adding New Built-in Tools

1. Create a new tool class inheriting from `BuiltinToolBase`:
```python
from HelpingAI.tools.builtin_tools.base import BuiltinToolBase

class MyCustomTool(BuiltinToolBase):
    name = "my_custom_tool"
    description = "Description of my custom tool"
    parameters = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter 1"}
        },
        "required": ["param1"]
    }
    
    def execute(self, **kwargs):
        # Tool implementation
        return "Tool result"
```

2. Register it in the registry:
```python
from HelpingAI.tools.builtin_tools import BUILTIN_TOOLS_REGISTRY
BUILTIN_TOOLS_REGISTRY['my_custom_tool'] = MyCustomTool
```

### Configuring Tool Behavior

Most tools accept configuration options:

```python
from HelpingAI.tools.builtin_tools.code_interpreter import CodeInterpreterTool

# Configure timeout and working directory
tool = CodeInterpreterTool({
    'timeout': 60,  # 60 seconds
    'work_dir': '/custom/work/dir'
})
```

## Dependencies

### Required
- No additional dependencies for basic functionality
- All built-in tools work with Python standard library

### Optional (Enhances functionality)
- `matplotlib`, `numpy`, `pandas`: For enhanced code interpreter capabilities
- `seaborn`: For advanced plotting in code interpreter
- `mcp`: For MCP server integration (separate from built-in tools)

## Best Practices

1. **Mix tool types appropriately**: Use MCP servers for external services, built-in tools for common tasks, and custom tools for domain-specific needs.

2. **Handle missing dependencies gracefully**: Built-in tools degrade gracefully when optional dependencies are missing.

3. **Use specific tools**: Instead of enabling all tools, select only the tools relevant to your use case.

4. **Configure timeouts**: For code interpreter, set appropriate timeouts based on expected execution time.

5. **Error handling**: Always handle `ToolExecutionError` and `ValueError` exceptions when using tools programmatically.

## Examples and Demos

See `examples/mcp_example.py` for complete examples demonstrating:
- Mixed MCP + built-in tools configuration
- Individual tool demonstrations
- Error handling patterns
- Advanced usage scenarios

## Compatibility

- ✅ Works with existing MCP infrastructure
- ✅ Compatible with OpenAI tool calling format
- ✅ Backward compatible with existing tool configurations
- ✅ No breaking changes to existing APIs
- ✅ Python 3.7+ support