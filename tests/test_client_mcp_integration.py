"""Test the complete integration flow with the HelpingAI client."""

import unittest
from unittest.mock import patch, MagicMock
import sys


class TestClientMCPIntegration(unittest.TestCase):
    """Test MCP integration with the HelpingAI client."""

    def test_client_tools_parameter_structure(self):
        """Test that the client's tools parameter accepts MCP structure."""
        
        # Just test that the tools parameter structure is accepted without errors
        from HelpingAI import HAI
        
        client = HAI(api_key="test-key")
        
        # User's exact MCP configuration structure
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
        
        # This should validate the structure without errors
        # We'll test this by checking if the conversion function handles it
        from HelpingAI.tools.compatibility import ensure_openai_format
        
        try:
            result = ensure_openai_format(tools)
            # Should fail with import error about mcp package, not structure error
            self.fail("Should have raised ImportError")
        except ImportError as e:
            # This is expected - MCP package not available
            self.assertIn('Could not import mcp', str(e))
        except ValueError as e:
            # This would indicate a structure problem - should not happen
            self.fail(f"Structure validation failed: {e}")

    def test_mixed_tools_structure(self):
        """Test mixed MCP and regular tools structure."""
        
        from HelpingAI.tools.compatibility import ensure_openai_format
        
        # Regular tools should work fine
        regular_tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform calculations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string"}
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]
        
        result = ensure_openai_format(regular_tools)
        self.assertEqual(result, regular_tools)
        
        # Mixed structure should handle regular tools and fail on MCP due to missing package
        mixed_tools = [
            {
                'mcpServers': {
                    'time': {
                        'command': 'uvx',
                        'args': ['mcp-server-time']
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform calculations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string"}
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]
        
        try:
            result = ensure_openai_format(mixed_tools)
            self.fail("Should have raised ImportError for MCP")
        except ImportError as e:
            self.assertIn('Could not import mcp', str(e))

    def test_configuration_validation_integration(self):
        """Test that configuration validation works through the whole stack."""
        
        # Test valid configuration through the manager
        from HelpingAI.tools.mcp_manager import MCPManager
        
        # Create manager without initialization to test validation only
        manager = object.__new__(MCPManager)
        
        # User's exact configuration
        user_config = {
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
        
        # Should validate correctly
        self.assertTrue(manager.is_valid_mcp_servers_config(user_config))
        
        # Invalid config should fail
        invalid_config = {
            'mcpServers': 'not_a_dict'
        }
        
        self.assertFalse(manager.is_valid_mcp_servers_config(invalid_config))


if __name__ == "__main__":
    unittest.main()