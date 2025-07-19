#!/usr/bin/env python3
"""
HelpingAI Tool Usage Examples

This script demonstrates proper usage patterns for the HelpingAI client,
specifically addressing common issues with tool configuration and API requests.

Common Issues Addressed:
1. Tool conversion errors - "Unsupported tools format"
2. HTTP 400 errors suggesting stream=True
3. Proper tool format specifications
"""

import os
import sys

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HelpingAI import HAI

def example_built_in_tools():
    """Example: Using built-in tools correctly."""
    print("=== Example 1: Built-in Tools ===")
    
    client = HAI(api_key=os.getenv("HAI_API_KEY", "your-api-key"))
    
    # ✅ CORRECT: Use built-in tool names as strings
    tools = ["code_interpreter", "web_search"]
    
    try:
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[{"role": "user", "content": "What's 2+2 and search for Python tutorials?"}],
            tools=tools,
            stream=False  # Try stream=True if you get HTTP 400 errors
        )
        print("✅ Request successful with built-in tools")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "400" in str(e) and "stream" in str(e).lower():
            print("💡 Tip: Try setting stream=True")

def example_openai_format_tools():
    """Example: Using OpenAI-format tools correctly."""
    print("\n=== Example 2: OpenAI Format Tools ===")
    
    client = HAI(api_key=os.getenv("HAI_API_KEY", "your-api-key"))
    
    # ✅ CORRECT: OpenAI tool format
    tools = [
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
            messages=[{"role": "user", "content": "Calculate 15 * 23"}],
            tools=tools
        )
        print("✅ Request successful with OpenAI format tools")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_mcp_tools():
    """Example: Using MCP (Model Context Protocol) tools correctly."""
    print("\n=== Example 3: MCP Tools ===")
    
    client = HAI(api_key=os.getenv("HAI_API_KEY", "your-api-key"))
    
    # ✅ CORRECT: MCP server configuration
    tools = [
        {
            'mcpServers': {
                'time': {
                    'command': 'uvx',
                    'args': ['mcp-server-time']
                },
                'fetch': {
                    'command': 'uvx',
                    'args': ['mcp-server-fetch']
                }
            }
        }
    ]
    
    try:
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[{"role": "user", "content": "What time is it?"}],
            tools=tools
        )
        print("✅ Request successful with MCP tools")
        
    except ImportError:
        print("❌ MCP dependencies not installed. Run: pip install 'HelpingAI[mcp]'")
    except Exception as e:
        print(f"❌ Error: {e}")

def example_mixed_tools():
    """Example: Mixing different tool types correctly."""
    print("\n=== Example 4: Mixed Tools ===")
    
    client = HAI(api_key=os.getenv("HAI_API_KEY", "your-api-key"))
    
    # ✅ CORRECT: Mix built-in tools with OpenAI format
    tools = [
        "code_interpreter",  # Built-in tool
        {
            "type": "function",
            "function": {
                "name": "custom_tool",
                "description": "A custom tool",
                "parameters": {"type": "object", "properties": {}}
            }
        }
    ]
    
    try:
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[{"role": "user", "content": "Help me with coding"}],
            tools=tools
        )
        print("✅ Request successful with mixed tools")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_streaming_usage():
    """Example: Using streaming to avoid HTTP 400 errors."""
    print("\n=== Example 5: Streaming Usage ===")
    
    client = HAI(api_key=os.getenv("HAI_API_KEY", "your-api-key"))
    
    try:
        # If you get HTTP 400 errors, try streaming
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[{"role": "user", "content": "Tell me a story"}],
            tools=["web_search"],
            stream=True  # 🔑 KEY: Enable streaming
        )
        
        print("✅ Streaming request initiated")
        
        # Process streaming response
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")
        print("\n✅ Streaming completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def common_mistakes():
    """Examples of common mistakes to avoid."""
    print("\n=== Common Mistakes to Avoid ===")
    
    # ❌ WRONG: Invalid tool names
    print("❌ DON'T: Use invalid built-in tool names")
    print("   tools = ['invalid_tool']  # Will cause warnings")
    
    # ❌ WRONG: Wrong data types
    print("❌ DON'T: Use wrong data types for tools")
    print("   tools = [1, 2, 3]  # Will cause warnings")
    
    # ❌ WRONG: Incorrect format
    print("❌ DON'T: Use incorrect tool format")
    print("   tools = {'not': 'a list'}  # Should be a list")
    
    # ✅ CORRECT alternatives
    print("\n✅ DO: Use correct formats")
    print("   tools = ['code_interpreter', 'web_search']  # Built-in tools")
    print("   tools = [{'type': 'function', ...}]  # OpenAI format")
    print("   tools = [{'mcpServers': {...}}]  # MCP format")

def troubleshooting_tips():
    """Troubleshooting tips for common issues."""
    print("\n=== Troubleshooting Tips ===")
    
    print("🔧 If you see 'Tool conversion failed' warnings:")
    print("   - Check that tool names are correct (code_interpreter, web_search)")
    print("   - Ensure tools are in proper format (list of strings/dicts)")
    print("   - For MCP tools, install: pip install 'HelpingAI[mcp]'")
    
    print("\n🔧 If you get HTTP 400 'stream=True' errors:")
    print("   - Try setting stream=True in your request")
    print("   - Some models/endpoints require streaming")
    print("   - Tool-heavy requests often need streaming")
    
    print("\n🔧 If you get 'Unknown built-in tool' errors:")
    print("   - Available built-in tools: code_interpreter, web_search")
    print("   - For custom tools, use OpenAI format with 'type': 'function'")
    
    print("\n🔧 For MCP tools:")
    print("   - Install MCP dependencies: pip install 'HelpingAI[mcp]'")
    print("   - Ensure MCP servers are properly configured")
    print("   - Check server commands and arguments")

if __name__ == "__main__":
    print("HelpingAI Tool Usage Examples")
    print("=" * 40)
    
    # Set up API key check
    if not os.getenv("HAI_API_KEY"):
        print("⚠️  Set HAI_API_KEY environment variable to run actual requests")
        print("   Examples will show structure without making API calls")
        print()
    
    # Run examples
    example_built_in_tools()
    example_openai_format_tools()
    example_mcp_tools()
    example_mixed_tools()
    example_streaming_usage()
    
    # Show common mistakes and tips
    common_mistakes()
    troubleshooting_tips()
    
    print("\n✅ For more examples, see: examples/mcp_example.py")
    print("📚 Documentation: https://helpingai.co/docs")