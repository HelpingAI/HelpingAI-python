"""
MCP (Multi-Channel Protocol) Integration Example

This example demonstrates how to use MCP servers with the HelpingAI SDK.
"""

from HelpingAI import HAI


def example_mcp_usage():
    """Example of using MCP servers with HelpingAI SDK."""
    
    # Initialize the client
    client = HAI(api_key="your-api-key")
    
    # Define MCP servers configuration
    # This is the exact format requested by the user
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
    
    # Create a chat completion with MCP tools
    try:
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[
                {"role": "user", "content": "What time is it in Shanghai?"}
            ],
            tools=tools  # MCP servers will be automatically initialized and converted to tools
        )
        
        print("Response:", response.choices[0].message.content)
        
        # If the model decides to use tools, tool_calls will be populated
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                print(f"Tool called: {tool_call.function.name}")
                print(f"Arguments: {tool_call.function.arguments}")
        
    except ImportError as e:
        print(f"MCP package not available: {e}")
        print("Install with: pip install -U mcp")
    except Exception as e:
        print(f"Error: {e}")


def example_mixed_tools():
    """Example of mixing MCP servers with regular tools."""
    
    client = HAI(api_key="your-api-key")
    
    # Mix MCP servers with regular OpenAI-format tools
    tools = [
        # MCP servers configuration
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
                "description": "Perform basic math calculations",
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
    
    try:
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[
                {"role": "user", "content": "What time is it and what is 2+2?"}
            ],
            tools=tools
        )
        
        print("Response:", response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error: {e}")


def example_advanced_mcp_config():
    """Example of advanced MCP server configurations."""
    
    tools = [
        {
            'mcpServers': {
                # Stdio-based server with environment variables
                'database': {
                    'command': 'python',
                    'args': ['-m', 'my_db_server'],
                    'env': {
                        'DB_URL': 'postgresql://user:pass@localhost/db',
                        'DB_TIMEOUT': '30'
                    }
                },
                # HTTP-based server (SSE)
                'remote_api': {
                    'url': 'https://api.example.com/mcp',
                    'headers': {
                        'Authorization': 'Bearer your-token',
                        'Accept': 'text/event-stream'
                    },
                    'sse_read_timeout': 300
                },
                # Streamable HTTP server
                'streamable_server': {
                    'type': 'streamable-http',
                    'url': 'http://localhost:8000/mcp'
                }
            }
        }
    ]
    
    print("Advanced MCP configuration:")
    print("- Stdio server with environment variables")
    print("- HTTP SSE server with authentication")
    print("- Streamable HTTP server")
    
    # Configuration is ready to use with client.chat.completions.create()


if __name__ == "__main__":
    print("=== HelpingAI MCP Integration Examples ===\n")
    
    print("1. Basic MCP Usage:")
    example_mcp_usage()
    print()
    
    print("2. Mixed Tools Example:")
    example_mixed_tools()
    print()
    
    print("3. Advanced MCP Configuration:")
    example_advanced_mcp_config()