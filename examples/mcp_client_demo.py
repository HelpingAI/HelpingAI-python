"""
Example MCP Client Usage

This demonstrates how to use the MCP client to interact with an MCP server
and call remote tools.
"""

import json
import time
from HelpingAI.mcp_client import MCPClient, create_client, quick_call, list_remote_tools


def demo_basic_client():
    """Demonstrate basic client functionality."""
    print("=== Basic MCP Client Demo ===")
    
    # Create client
    client = create_client("http://localhost:8000")
    
    try:
        # Test connection
        print("1. Testing server connection...")
        if client.ping():
            print("✓ Server is reachable")
        else:
            print("✗ Server is not reachable")
            return
        
        # Get server info
        print("\n2. Getting server information...")
        server_info = client.get_server_info()
        print(f"   Status: {server_info['status']}")
        print(f"   Tools count: {server_info['tools_count']}")
        
        # List available tools
        print("\n3. Listing available tools...")
        tools = client.list_tools()
        print(f"   Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # Test some tools
        print("\n4. Testing tools...")
        
        # Test mathematical operations
        if client.tool_exists('add'):
            result = client.call_tool('add', {'a': 5, 'b': 3})
            print(f"   add(5, 3) = {result}")
        
        if client.tool_exists('multiply'):
            result = client.call_tool('multiply', {'a': 4, 'b': 7})
            print(f"   multiply(4, 7) = {result}")
        
        if client.tool_exists('calculate_circle_area'):
            result = client.call_tool('calculate_circle_area', {'radius': 5})
            print(f"   circle_area(radius=5) = {result:.2f}")
        
        # Test string operations
        if client.tool_exists('reverse_string'):
            result = client.call_tool('reverse_string', {'text': 'Hello MCP!'})
            print(f"   reverse_string('Hello MCP!') = '{result}'")
        
        if client.tool_exists('count_words'):
            result = client.call_tool('count_words', {'text': 'This is a test sentence'})
            print(f"   count_words('This is a test sentence') = {result}")
        
        # Test complex tool with dict result
        if client.tool_exists('calculate_tip'):
            result = client.call_tool('calculate_tip', {'bill_amount': 50.0, 'tip_percentage': 20.0})
            print(f"   calculate_tip(bill=50, tip=20%) = {json.dumps(result, indent=2)}")
        
        # Test utility tools
        if client.tool_exists('get_current_time'):
            result = client.call_tool('get_current_time', {})
            print(f"   get_current_time() = {result}")
        
        if client.tool_exists('greet_user'):
            result = client.call_tool('greet_user', {'name': 'Alice', 'greeting': 'Hi'})
            print(f"   greet_user(name='Alice', greeting='Hi') = '{result}'")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_convenience_functions():
    """Demonstrate convenience functions."""
    print("\n=== Convenience Functions Demo ===")
    
    try:
        # Quick tool listing
        print("1. Quick tool listing...")
        tools = list_remote_tools()
        print(f"   Found {len(tools)} tools using quick function")
        
        # Quick tool calls
        print("\n2. Quick tool calls...")
        result = quick_call('add', {'a': 10, 'b': 20})
        print(f"   quick_call('add', {{'a': 10, 'b': 20}}) = {result}")
        
        result = quick_call('reverse_string', {'text': 'MCP is awesome!'})
        print(f"   quick_call('reverse_string', {{'text': 'MCP is awesome!'}}) = '{result}'")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n=== Error Handling Demo ===")
    
    client = create_client("http://localhost:8000")
    
    try:
        # Test calling non-existent tool
        print("1. Testing non-existent tool...")
        try:
            client.call_tool('non_existent_tool', {})
        except Exception as e:
            print(f"   Expected error: {e}")
        
        # Test invalid arguments
        print("\n2. Testing invalid arguments...")
        if client.tool_exists('calculate_circle_area'):
            try:
                client.call_tool('calculate_circle_area', {'radius': -5})
            except Exception as e:
                print(f"   Expected error: {e}")
        
        # Test malformed arguments
        print("\n3. Testing malformed arguments...")
        if client.tool_exists('add'):
            try:
                client.call_tool('add', {'a': 'not_a_number', 'b': 5})
            except Exception as e:
                print(f"   Expected error: {e}")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demo_tool_discovery():
    """Demonstrate tool discovery features."""
    print("\n=== Tool Discovery Demo ===")
    
    client = create_client("http://localhost:8000")
    
    try:
        # Discover all tools
        print("1. Discovering tools...")
        tools_map = client.discover_tools()
        print(f"   Discovered {len(tools_map)} tools")
        
        # Get detailed info for specific tools
        print("\n2. Tool details...")
        for tool_name in ['add', 'calculate_tip', 'greet_user']:
            if tool_name in tools_map:
                tool_info = tools_map[tool_name]
                print(f"   {tool_name}:")
                print(f"     Description: {tool_info['description']}")
                print(f"     Parameters: {json.dumps(tool_info['parameters'], indent=6)}")
        
        # Check tool existence
        print("\n3. Checking tool existence...")
        test_tools = ['add', 'subtract', 'multiply', 'divide']
        for tool_name in test_tools:
            exists = client.tool_exists(tool_name)
            print(f"   {tool_name}: {'✓' if exists else '✗'}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def interactive_mode():
    """Interactive mode for testing tools."""
    print("\n=== Interactive Mode ===")
    print("Type 'list' to see tools, 'call <tool_name> <json_args>' to call a tool, 'quit' to exit")
    
    client = create_client("http://localhost:8000")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            elif command.lower() == 'list':
                tools = client.list_tools()
                print(f"Available tools ({len(tools)}):")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
            elif command.startswith('call '):
                parts = command[5:].split(' ', 1)
                tool_name = parts[0]
                
                if len(parts) > 1:
                    try:
                        args = json.loads(parts[1])
                    except json.JSONDecodeError:
                        print("Error: Invalid JSON arguments")
                        continue
                else:
                    args = {}
                
                try:
                    result = client.call_tool(tool_name, args)
                    print(f"Result: {json.dumps(result, indent=2)}")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Unknown command. Try 'list', 'call <tool> <args>', or 'quit'")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")


def main():
    """Run all demos."""
    print("MCP Client Demo")
    print("===============")
    print("Make sure the MCP server is running on http://localhost:8000")
    print("You can start it with: python examples/mcp_server_demo.py")
    
    # Wait a moment for user to read
    time.sleep(2)
    
    # Run demos
    demo_basic_client()
    demo_convenience_functions()
    demo_error_handling()
    demo_tool_discovery()
    
    # Ask if user wants interactive mode
    try:
        response = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_mode()
    except KeyboardInterrupt:
        print("\nDemo completed!")


if __name__ == "__main__":
    main()