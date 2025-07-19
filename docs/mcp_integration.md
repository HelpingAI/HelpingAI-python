# MCP (Multi-Channel Protocol) Integration

The HelpingAI SDK now supports MCP (Model Context  Protocol) servers, allowing you to easily integrate external tools and services into your AI applications.

## Installation

To use MCP functionality, install the MCP package:

```bash
pip install -U mcp
```

Or install HelpingAI with MCP support:

```bash
pip install HelpingAI[mcp]
```

## Basic Usage

Use MCP servers by including them in the `tools` parameter of your chat completion:

```python
from HelpingAI import HAI

client = HAI(api_key="your-api-key")

# Define MCP servers
tools = [
    {
        'mcpServers': {
            'time': {
                'command': 'uvx',
                'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
            },
            'fetch': {
                'command': 'uvx',
                'args': ['mcp-server-fetch']
            }
        }
    }
]

# Use in chat completion
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "What time is it in Shanghai?"}
    ],
    tools=tools
)
```

## Configuration Options

### Stdio-based Servers

Most MCP servers use stdio for communication:

```python
{
    'mcpServers': {
        'server_name': {
            'command': 'executable_name',
            'args': ['arg1', 'arg2'],
            'env': {  # Optional environment variables
                'ENV_VAR': 'value'
            }
        }
    }
}
```

### HTTP-based Servers (SSE)

For HTTP servers using Server-Sent Events:

```python
{
    'mcpServers': {
        'remote_server': {
            'url': 'https://api.example.com/mcp',
            'headers': {  # Optional headers
                'Authorization': 'Bearer token',
                'Accept': 'text/event-stream'
            },
            'sse_read_timeout': 300  # Optional timeout in seconds
        }
    }
}
```

### Streamable HTTP Servers

For streamable HTTP servers:

```python
{
    'mcpServers': {
        'streamable_server': {
            'type': 'streamable-http',
            'url': 'http://localhost:8000/mcp'
        }
    }
}
```

## Mixed Tool Usage

You can combine MCP servers with regular OpenAI-format tools:

```python
tools = [
    # MCP servers
    {
        'mcpServers': {
            'time': {
                'command': 'uvx',
                'args': ['mcp-server-time']
            }
        }
    },
    # Regular OpenAI-format tool
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform math calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]
```


## Resources

MCP servers can also provide resources (read-only data sources). When a server has resources, the SDK automatically adds:

- `{server_name}-list_resources`: List available resources
- `{server_name}-read_resource`: Read a specific resource by URI

## Error Handling

The SDK handles MCP errors gracefully:

```python
try:
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "What time is it?"}],
        tools=tools
    )
except ImportError:
    print("MCP package not installed. Run: pip install -U mcp")
except Exception as e:
    print(f"Error: {e}")
```

## Advanced Features

### Automatic Reconnection

The SDK automatically handles MCP server disconnections and attempts to reconnect when needed.

### Process Management

MCP server processes are automatically managed and cleaned up when your application exits.

### Tool Naming

MCP tools are automatically named with the format: `{server_name}-{tool_name}` to avoid conflicts.

## Limitations

- MCP servers must be installed and available in your environment
- Some servers may require specific permissions or environment setup
- Network-based servers require appropriate network access

## Examples

See the `examples/mcp_example.py` file for comprehensive usage examples.