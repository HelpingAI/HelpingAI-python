#!/usr/bin/env python3
"""
Test tool conversion without making actual API calls.
"""

from HelpingAI import HAI

def test_tool_conversion():
    """Test the tool conversion process without API calls."""
    
    client = HAI(api_key="test-key")
    
    # The problematic configuration from the issue
    tools = [
        {'mcpServers': {
            'time': {'command': 'uvx', 'args': ['mcp-server-time']},
            'fetch': {'command': 'uvx', 'args': ['mcp-server-fetch']},
            'ddg-search': {
                'command': 'npx',
                'args': ['-y', '@oevortex/ddg_search@latest']
            }
        }},
        'code_interpreter',
    ]
    
    print("Testing tool conversion process...")
    
    # Test the conversion directly
    try:
        converted_tools = client._convert_tools_parameter(tools)
        
        if converted_tools:
            print(f"✅ Tool conversion successful! Converted {len(converted_tools)} tools:")
            for i, tool in enumerate(converted_tools):
                tool_name = tool.get('function', {}).get('name', 'Unknown')
                print(f"  {i+1}. {tool_name}")
        else:
            print("❌ Tool conversion returned None")
            
    except Exception as e:
        print(f"❌ Tool conversion failed: {e}")

if __name__ == "__main__":
    test_tool_conversion()