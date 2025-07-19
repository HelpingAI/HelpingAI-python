"""Test MCP (Multi-Channel Protocol) integration."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from typing import Dict, Any, List

import sys


class TestMCPClient(unittest.TestCase):
    """Test MCP client functionality."""

    def test_mcp_client_init_without_mcp(self):
        """Test MCP client initialization without mcp package."""
        # Mock the import to fail
        with patch.dict('sys.modules', {'mcp': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'mcp'")):
                from HelpingAI.tools.mcp_client import MCPClient
                with self.assertRaises(ImportError) as cm:
                    MCPClient()
                self.assertIn('Could not import mcp', str(cm.exception))

    def test_mcp_client_with_mock_mcp(self):
        """Test MCP client initialization with mocked mcp package."""
        # Mock the mcp module
        mock_mcp = MagicMock()
        mock_client_session = MagicMock()
        mock_mcp.ClientSession = mock_client_session
        
        with patch.dict('sys.modules', {'mcp': mock_mcp}):
            from HelpingAI.tools.mcp_client import MCPClient
            client = MCPClient()
            self.assertIsNone(client.session)
            self.assertEqual(client.tools, [])
            self.assertFalse(client.resources)


class TestMCPManager(unittest.TestCase):
    """Test MCP manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset the singleton
        if 'HelpingAI.tools.mcp_manager' in sys.modules:
            manager_module = sys.modules['HelpingAI.tools.mcp_manager']
            if hasattr(manager_module, 'MCPManager'):
                manager_module.MCPManager._instance = None

    def test_mcp_manager_without_mcp_package(self):
        """Test MCP manager fails gracefully without mcp package."""
        with patch.dict('sys.modules', {'mcp': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'mcp'")):
                from HelpingAI.tools.mcp_manager import MCPManager
                with self.assertRaises(ImportError) as cm:
                    MCPManager()
                self.assertIn('Could not import mcp', str(cm.exception))

    def test_mcp_manager_singleton_with_mock(self):
        """Test MCP manager singleton pattern with mocked mcp."""
        mock_mcp = MagicMock()
        
        with patch.dict('sys.modules', {'mcp': mock_mcp}):
            from HelpingAI.tools.mcp_manager import MCPManager
            manager1 = MCPManager()
            manager2 = MCPManager()
            self.assertIs(manager1, manager2)

    def test_valid_mcp_servers_config(self):
        """Test MCP servers configuration validation."""
        mock_mcp = MagicMock()
        
        with patch.dict('sys.modules', {'mcp': mock_mcp}):
            from HelpingAI.tools.mcp_manager import MCPManager
            manager = MCPManager()
            
            # Valid configuration
            valid_config = {
                "mcpServers": {
                    "time": {
                        "command": "uvx",
                        "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
                    },
                    "fetch": {
                        "command": "uvx",
                        "args": ["mcp-server-fetch"]
                    }
                }
            }
            self.assertTrue(manager.is_valid_mcp_servers_config(valid_config))

    def test_invalid_mcp_servers_config(self):
        """Test invalid MCP servers configuration."""
        mock_mcp = MagicMock()
        
        with patch.dict('sys.modules', {'mcp': mock_mcp}):
            from HelpingAI.tools.mcp_manager import MCPManager
            manager = MCPManager()
            
            # Invalid configurations
            invalid_configs = [
                {},  # Missing mcpServers key
                {"mcpServers": "not_a_dict"},  # mcpServers not a dict
                {"mcpServers": {"server": "not_a_dict"}},  # Server config not a dict
                {"mcpServers": {"server": {"command": 123}}},  # Invalid command type
                {"mcpServers": {"server": {"command": "uvx", "args": "not_a_list"}}},  # Invalid args type
            ]
            
            for config in invalid_configs:
                with self.subTest(config=config):
                    self.assertFalse(manager.is_valid_mcp_servers_config(config))


class TestMCPCompatibility(unittest.TestCase):
    """Test MCP integration with the compatibility system."""

    def test_ensure_openai_format_with_mcp_servers(self):
        """Test ensure_openai_format handles MCP servers configuration."""
        # Mock MCP functionality
        mock_mcp = MagicMock()
        mock_manager = MagicMock()
        mock_tools = [
            MagicMock(name="time-get_current_time", description="Get current time", parameters={})
        ]
        mock_manager.init_config.return_value = mock_tools
        
        with patch.dict('sys.modules', {'mcp': mock_mcp}):
            # Import and patch the MCP manager in compatibility module
            with patch('HelpingAI.tools.compatibility.MCPManager', return_value=mock_manager):
                from HelpingAI.tools.compatibility import ensure_openai_format
                
                # Mock _convert_fns_to_tools
                with patch('HelpingAI.tools.compatibility._convert_fns_to_tools') as mock_convert:
                    mock_convert.return_value = [
                        {
                            "type": "function",
                            "function": {
                                "name": "time-get_current_time",
                                "description": "Get current time",
                                "parameters": {}
                            }
                        }
                    ]
                    
                    tools_config = [
                        {
                            "mcpServers": {
                                "time": {
                                    "command": "uvx",
                                    "args": ["mcp-server-time"]
                                }
                            }
                        }
                    ]
                    
                    result = ensure_openai_format(tools_config)
                    
                    # Verify result
                    self.assertIsInstance(result, list)
                    self.assertEqual(len(result), 1)
                    self.assertEqual(result[0]["type"], "function")
                    self.assertEqual(result[0]["function"]["name"], "time-get_current_time")

    def test_ensure_openai_format_mixed_tools(self):
        """Test ensure_openai_format handles mixed MCP and regular tools."""
        mock_mcp = MagicMock()
        mock_manager = MagicMock()
        mock_manager.init_config.return_value = []
        
        with patch.dict('sys.modules', {'mcp': mock_mcp}):
            with patch('HelpingAI.tools.compatibility.MCPManager', return_value=mock_manager):
                from HelpingAI.tools.compatibility import ensure_openai_format
                
                with patch('HelpingAI.tools.compatibility._convert_fns_to_tools') as mock_convert:
                    mock_convert.return_value = []
                    
                    mixed_tools = [
                        {
                            "mcpServers": {
                                "time": {
                                    "command": "uvx",
                                    "args": ["mcp-server-time"]
                                }
                            }
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "regular_tool",
                                "description": "A regular tool",
                                "parameters": {}
                            }
                        }
                    ]
                    
                    result = ensure_openai_format(mixed_tools)
                    
                    # Should contain both MCP tools and regular tools
                    self.assertIsInstance(result, list)
                    # Check that regular tool is preserved
                    regular_tools = [tool for tool in result if tool.get("function", {}).get("name") == "regular_tool"]
                    self.assertEqual(len(regular_tools), 1)

    def test_ensure_openai_format_without_mcp_package(self):
        """Test ensure_openai_format handles missing MCP package gracefully."""
        with patch.dict('sys.modules', {'mcp': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'mcp'")):
                from HelpingAI.tools.compatibility import ensure_openai_format
                
                tools_config = [
                    {
                        "mcpServers": {
                            "time": {
                                "command": "uvx",
                                "args": ["mcp-server-time"]
                            }
                        }
                    }
                ]
                
                with self.assertRaises(ImportError) as cm:
                    ensure_openai_format(tools_config)
                
                self.assertIn('MCP functionality requires', str(cm.exception))


class TestMCPIntegration(unittest.TestCase):
    """Integration tests for MCP functionality."""

    def test_mcp_config_validation_comprehensive(self):
        """Test comprehensive MCP configuration validation."""
        mock_mcp = MagicMock()
        
        with patch.dict('sys.modules', {'mcp': mock_mcp}):
            from HelpingAI.tools.mcp_manager import MCPManager
            manager = MCPManager()
            
            # Test various valid configurations
            valid_configs = [
                # Basic stdio configuration
                {
                    "mcpServers": {
                        "time": {
                            "command": "uvx",
                            "args": ["mcp-server-time"]
                        }
                    }
                },
                # Configuration with environment variables
                {
                    "mcpServers": {
                        "db": {
                            "command": "python",
                            "args": ["-m", "db_server"],
                            "env": {"DB_URL": "sqlite:///test.db"}
                        }
                    }
                },
                # URL-based configuration
                {
                    "mcpServers": {
                        "remote": {
                            "url": "https://example.com/mcp",
                            "headers": {"Authorization": "Bearer token"}
                        }
                    }
                },
                # Multiple servers
                {
                    "mcpServers": {
                        "time": {
                            "command": "uvx",
                            "args": ["mcp-server-time"]
                        },
                        "fetch": {
                            "command": "uvx",
                            "args": ["mcp-server-fetch"]
                        }
                    }
                }
            ]
            
            for config in valid_configs:
                with self.subTest(config=config):
                    self.assertTrue(manager.is_valid_mcp_servers_config(config))

    def test_user_example_configuration(self):
        """Test the exact configuration format requested by the user."""
        mock_mcp = MagicMock()
        
        with patch.dict('sys.modules', {'mcp': mock_mcp}):
            from HelpingAI.tools.mcp_manager import MCPManager
            manager = MCPManager()
            
            # User's exact example
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
            
            # Should validate successfully
            self.assertTrue(manager.is_valid_mcp_servers_config(user_config))


if __name__ == "__main__":
    unittest.main()