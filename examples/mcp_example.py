"""
MCP (Model Context Protocol) Integration Example with Built-in Tools

This example demonstrates how to use both MCP servers and built-in tools 
with the HelpingAI SDK.
"""

from HelpingAI import HAI


def example_mixed_tools_usage():
    """Example of using both MCP servers and built-in tools together."""
    
    # Initialize the client
    client = HAI(api_key="your-api-key")
    
    # Define mixed tools configuration - exactly as requested by the user
    tools = [
        {
            'mcpServers': {  # MCP servers configuration
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
        'web_search'
    ]
    
    # Create a chat completion with mixed tools
    try:
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[
                {"role": "user", "content": "Search for Python tutorials and then write a simple Python script"}
            ],
            tools=tools  # Mix of MCP servers and built-in tools
        )
        
        print("Response:", response.choices[0].message.content)
        
        # If the model decides to use tools, tool_calls will be populated
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                print(f"Tool called: {tool_call.function.name}")
                print(f"Arguments: {tool_call.function.arguments}")
        
    except ImportError as e:
        if 'mcp' in str(e):
            print("MCP package not available, testing built-in tools only...")
            example_builtin_tools_only()
        else:
            raise
    except Exception as e:
        print(f"Error: {e}")


def example_builtin_tools_only():
    """Example using only built-in tools (no MCP dependency)."""
    
    client = HAI(api_key="your-api-key")
    
    # Use only built-in tools - no MCP dependency required
    tools = [
        'code_interpreter',  # Execute Python code
        'web_search',        # Search the web
    ]
    
    try:
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[
                {"role": "user", "content": "Write a Python script to calculate fibonacci numbers"}
            ],
            tools=tools
        )
        
        print("Response:", response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error: {e}")


def example_specific_builtin_tools():
    """Example using specific built-in tools."""
    
    client = HAI(api_key="your-api-key")
    
    # Use only specific built-in tools
    tools = ['code_interpreter', 'web_search']
    
    try:
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[
                {"role": "user", "content": "Search for machine learning tutorials and create a simple example"}
            ],
            tools=tools
        )
        
        print("Response:", response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error: {e}")


def demonstrate_builtin_tools():
    """Demonstrate the available built-in tools."""
    
    from HelpingAI.tools import get_available_builtin_tools
    
    print("=== Available Built-in Tools ===")
    available_tools = get_available_builtin_tools()
    
    for tool_name in available_tools:
        print(f"- {tool_name}")
    
    print(f"\nTotal: {len(available_tools)} built-in tools available")
    
    print("\n=== Tool Usage Examples ===")
    
    # Example 1: Code interpreter
    print("1. Code Interpreter:")
    from HelpingAI.tools.builtin_tools.code_interpreter import CodeInterpreterTool
    code_tool = CodeInterpreterTool()
    result = code_tool.execute(code="print('Hello, World!')\nresult = 2 ** 10\nprint(f'2^10 = {result}')")
    print(f"   Result: {result}")
    
    # Example 2: Web search
    print("\n2. Web Search:")
    from HelpingAI.tools.builtin_tools.web_search import WebSearchTool
    search_tool = WebSearchTool()
    result = search_tool.execute(query="artificial intelligence", max_results=2)
    print(f"   Result: {result[:200]}...")

def example_advanced_mixed_config():
    """Example of advanced configuration mixing all tool types."""
    
    tools = [
        # MCP servers configuration
        {
            'mcpServers': {
                'time': {
                    'command': 'uvx',
                    'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
                },
                "fetch": {
                    "command": "uvx", 
                    "args": ["mcp-server-fetch"]
                },
                # HTTP-based MCP server
                'remote_api': {
                    'url': 'https://api.example.com/mcp',
                    'headers': {
                        'Authorization': 'Bearer your-token'
                    }
                }
            }
        },
        # Built-in tools
        'code_interpreter',
        'web_search',
        # Regular OpenAI-format tool
        {
            "type": "function",
            "function": {
                "name": "custom_calculator",
                "description": "Perform custom calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    ]
    
    print("Advanced mixed configuration ready:")
    print("- MCP servers (3 servers)")
    print("- Built-in tools (2 tools)")
    print("- Custom OpenAI-format tool (1 tool)")
    print("\nTotal: Up to 6+ tools available for the AI model")


if __name__ == "__main__":
    print("=== HelpingAI SDK: MCP + Built-in Tools Integration ===\n")
    
    print("1. Demonstrating Built-in Tools:")
    demonstrate_builtin_tools()
    print()
    
    print("2. Mixed Tools Usage Example:")
    example_mixed_tools_usage()
    print()
    
    print("3. Built-in Tools Only Example:")
    example_builtin_tools_only()
    print()
    
    print("4. Specific Tools Example:")
    example_specific_builtin_tools()
    print()
    
    print("5. Advanced Mixed Configuration:")
    example_advanced_mixed_config()
    print()
    
    print("🎉 Examples completed!")