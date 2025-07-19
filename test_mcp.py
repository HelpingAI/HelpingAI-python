#!/usr/bin/env python3
"""
Test script for MCP-like server and client functionality.

This script tests the basic functionality of the MCP implementation
without requiring external dependencies.
"""

import json
import threading
import time
import unittest
from HelpingAI.tools import tools, clear_registry
from HelpingAI.mcp_server import MCPServer
from HelpingAI.mcp_client import MCPClient


# Test tools
@tools
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    return a + b


@tools
def greet(name: str, greeting: str = "Hello") -> str:
    """Generate a greeting message.
    
    Args:
        name: Person's name
        greeting: Greeting word
    """
    return f"{greeting}, {name}!"


@tools
def get_info() -> dict:
    """Get some test information."""
    return {
        "message": "This is a test",
        "timestamp": "2024-01-01T00:00:00",
        "version": "1.0.0"
    }


class TestMCPImplementation(unittest.TestCase):
    """Test cases for MCP server and client."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test server."""
        print("Starting test server...")
        cls.server = MCPServer('localhost', 8001)
        cls.server_thread = threading.Thread(target=cls.server.start, kwargs={'blocking': True})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        cls.client = MCPClient('http://localhost:8001')
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        print("Stopping test server...")
        if hasattr(cls, 'server'):
            cls.server.stop()
    
    def test_server_health(self):
        """Test server health check."""
        health = self.client.health_check()
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('tools_count', health)
    
    def test_list_tools(self):
        """Test listing tools."""
        tools = self.client.list_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check that our test tools are present
        tool_names = [tool['name'] for tool in tools]
        self.assertIn('add_numbers', tool_names)
        self.assertIn('greet', tool_names)
        self.assertIn('get_info', tool_names)
    
    def test_tool_discovery(self):
        """Test tool discovery features."""
        tools_map = self.client.discover_tools()
        self.assertIsInstance(tools_map, dict)
        
        # Check add_numbers tool details
        self.assertIn('add_numbers', tools_map)
        add_tool = tools_map['add_numbers']
        self.assertEqual(add_tool['name'], 'add_numbers')
        self.assertIn('parameters', add_tool)
        self.assertIn('description', add_tool)
    
    def test_call_simple_tool(self):
        """Test calling a simple mathematical tool."""
        result = self.client.call_tool('add_numbers', {'a': 5, 'b': 3})
        self.assertEqual(result, 8)
    
    def test_call_string_tool(self):
        """Test calling a string manipulation tool."""
        result = self.client.call_tool('greet', {'name': 'Alice'})
        self.assertEqual(result, 'Hello, Alice!')
        
        result = self.client.call_tool('greet', {'name': 'Bob', 'greeting': 'Hi'})
        self.assertEqual(result, 'Hi, Bob!')
    
    def test_call_dict_return_tool(self):
        """Test calling a tool that returns a dictionary."""
        result = self.client.call_tool('get_info', {})
        self.assertIsInstance(result, dict)
        self.assertIn('message', result)
        self.assertEqual(result['message'], 'This is a test')
    
    def test_tool_existence(self):
        """Test tool existence checking."""
        self.assertTrue(self.client.tool_exists('add_numbers'))
        self.assertTrue(self.client.tool_exists('greet'))
        self.assertFalse(self.client.tool_exists('nonexistent_tool'))
    
    def test_error_handling(self):
        """Test error handling for invalid tool calls."""
        with self.assertRaises(Exception):
            self.client.call_tool('nonexistent_tool', {})
        
        # Test invalid arguments (string instead of number)
        with self.assertRaises(Exception):
            self.client.call_tool('add_numbers', {'a': 'not_a_number', 'b': 5})


def run_basic_functionality_test():
    """Run a simple end-to-end test without unittest framework."""
    print("=== Basic Functionality Test ===")
    
    # Ensure tools are registered
    from HelpingAI.tools import get_tools
    tools_list = get_tools()
    print(f"Registered tools: {[t.name for t in tools_list]}")
    
    # Start server in separate thread
    print("1. Starting test server...")
    server = MCPServer('localhost', 8002)
    server_thread = threading.Thread(target=server.start, kwargs={'blocking': True})
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Test client functionality
        print("2. Testing client connection...")
        client = MCPClient('http://localhost:8002')
        
        if not client.ping():
            print("✗ Server is not reachable")
            return False
        print("✓ Server is reachable")
        
        print("3. Testing tool discovery...")
        tools = client.list_tools()
        print(f"✓ Found {len(tools)} tools")
        
        print("4. Testing tool calls...")
        
        # Test mathematical operation
        result = client.call_tool('add_numbers', {'a': 10, 'b': 20})
        expected = 30
        if result == expected:
            print(f"✓ add_numbers(10, 20) = {result}")
        else:
            print(f"✗ add_numbers(10, 20) = {result}, expected {expected}")
            return False
        
        # Test string operation
        result = client.call_tool('greet', {'name': 'Test', 'greeting': 'Welcome'})
        expected = 'Welcome, Test!'
        if result == expected:
            print(f"✓ greet('Test', 'Welcome') = '{result}'")
        else:
            print(f"✗ greet('Test', 'Welcome') = '{result}', expected '{expected}'")
            return False
        
        # Test dictionary return
        result = client.call_tool('get_info', {})
        if isinstance(result, dict) and 'message' in result:
            print(f"✓ get_info() returned valid dict")
        else:
            print(f"✗ get_info() returned invalid result: {result}")
            return False
        
        print("✓ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        print("5. Stopping server...")
        server.stop()


def main():
    """Run all tests."""
    print("MCP Implementation Test Suite")
    print("=" * 40)
    
    # Register test tools (don't clear registry)
    print("Registering test tools...")
    
    # Run basic functionality test first
    basic_success = run_basic_functionality_test()
    
    if basic_success:
        print("\n" + "=" * 40)
        print("Running detailed unit tests...")
        print("=" * 40)
        
        # Run unit tests
        unittest.main(argv=[''], exit=False, verbosity=2)
    else:
        print("\nBasic functionality test failed. Skipping unit tests.")


if __name__ == "__main__":
    main()