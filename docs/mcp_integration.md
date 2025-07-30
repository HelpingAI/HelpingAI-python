# MCP Integration Guide

This comprehensive guide explains how to integrate external tools and services using MCP (Model Context Protocol) servers with the HelpingAI Python SDK, including advanced features like automatic lifecycle management, enhanced workflow integration, and production-ready configurations.

## What is MCP?

The **Model Context Protocol (MCP)** is a standardized communication protocol that enables the HelpingAI SDK to interact seamlessly with external tool servers. MCP transforms your AI applications by providing access to a vast ecosystem of specialized tools, services, and data sources that extend far beyond the model's inherent knowledge.

### Key Benefits

- **Seamless Integration**: MCP tools work transparently alongside built-in tools like [`code_interpreter`](../HelpingAI/tools/builtin_tools/code_interpreter.py:1) and [`web_search`](../HelpingAI/tools/builtin_tools/web_search.py:1)
- **Automatic Lifecycle Management**: The SDK handles server connections, reconnections, and cleanup automatically
- **Enhanced Workflow Integration**: MCP tools benefit from automatic tool caching and the enhanced workflow system
- **Production Ready**: Built-in error handling, process management, and resource cleanup
- **Multiple Transport Protocols**: Support for stdio, SSE, and streamable HTTP connections
- **Resource Access**: Automatic discovery and access to MCP server resources and data sources

### How MCP Enhances Your Workflow

MCP facilitates a clear separation of concerns: your AI model focuses on reasoning and decision-making, while specialized MCP servers handle the execution of specific tasks. This modular approach enables:

1. **Real-time Data Access**: Connect to live APIs, databases, and external services
2. **Specialized Tool Execution**: Access domain-specific tools for file systems, development environments, and more
3. **Dynamic Resource Management**: Automatically discover and utilize available resources
4. **Scalable Architecture**: Add new capabilities without modifying your core application
5. **Mixed Tool Workflows**: Combine MCP tools with built-in tools for powerful multi-step operations

### Common Use Cases

- **Development Tools**: File system access, code execution, version control integration
- **Data Processing**: Database queries, API integrations, data transformation
- **System Operations**: Server monitoring, deployment automation, infrastructure management
- **Content Creation**: Document generation, image processing, media manipulation
- **Business Intelligence**: Analytics, reporting, dashboard creation

## Installation

To leverage the full capabilities of MCP integration, you need to install the `mcp` Python package. This package provides the necessary client-side components to communicate with MCP servers using various transport protocols.

### Recommended Installation

The easiest way to install `mcp` along with the HelpingAI SDK is by specifying the `mcp` extra during installation:

```bash
pip install "HelpingAI[mcp]"
```

This command ensures that all required dependencies for MCP functionality are installed automatically, including support for stdio, SSE, and streamable HTTP transports.

### Manual Installation

If you prefer to install `mcp` separately, you can do so using pip:

```bash
pip install -U mcp
```

For development or bleeding-edge features, you can install from the source:

```bash
pip install git+https://github.com/modelcontextprotocol/python-sdk.git
```

### Environment-Specific Installation

#### Virtual Environments (Recommended)

Using virtual environments prevents dependency conflicts and ensures clean installations:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install HelpingAI with MCP support
pip install "HelpingAI[mcp]"
```

#### Docker Environments

For containerized deployments, add MCP support to your Dockerfile:

```dockerfile
FROM python:3.9-slim

# Install HelpingAI with MCP support
RUN pip install "HelpingAI[mcp]"

# Install additional MCP server dependencies if needed
RUN pip install uvx  # For uvx-based MCP servers
```

#### Production Environments

For production deployments, pin specific versions for stability:

```bash
pip install "HelpingAI[mcp]==1.0.0" "mcp==0.9.0"
```

### Verifying Installation

After installation, verify that the `mcp` package is correctly installed:

```bash
python -c "import mcp; print(f'MCP version: {mcp.__version__}')"
```

Test HelpingAI MCP integration:

```python
from HelpingAI.tools.mcp_manager import MCPManager
print("MCP integration available!")
```

### MCP Server Dependencies

Many MCP servers require additional tools to be installed:

#### uvx (Universal Package Runner)

Required for many Python-based MCP servers:

```bash
pip install uvx
```

#### Node.js and npm

Required for JavaScript-based MCP servers:

```bash
# Install Node.js (varies by system)
# Ubuntu/Debian:
sudo apt-get install nodejs npm

# macOS:
brew install node

# Windows: Download from nodejs.org
```

### Troubleshooting

#### Common Installation Issues

**`ImportError: Could not import mcp`**
- **Cause**: MCP package not installed or not accessible
- **Solution**:
  ```bash
  pip install -U mcp
  # Or reinstall HelpingAI with MCP support
  pip install --force-reinstall "HelpingAI[mcp]"
  ```

**`ModuleNotFoundError: No module named 'mcp.client'`**
- **Cause**: Incomplete MCP installation
- **Solution**:
  ```bash
  pip uninstall mcp
  pip install "HelpingAI[mcp]"
  ```

**Dependency Conflicts**
- **Cause**: Conflicting package versions
- **Solution**: Use virtual environments or dependency resolution:
  ```bash
  pip install --upgrade-strategy eager "HelpingAI[mcp]"
  ```

#### Platform-Specific Issues

**Windows**
- Ensure Windows Subsystem for Linux (WSL) is available for stdio-based MCP servers
- Use PowerShell or Command Prompt with administrator privileges if needed

**macOS**
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for system dependencies: `brew install python`

**Linux**
- Install development headers: `sudo apt-get install python3-dev`
- Ensure proper permissions for process creation

#### Network and Firewall Issues

For HTTP-based MCP servers:
- Ensure outbound connections are allowed on required ports
- Configure proxy settings if behind corporate firewall:
  ```bash
  pip install --proxy http://proxy.company.com:port "HelpingAI[mcp]"
  ```

#### Performance Optimization

For better performance in production:

```bash
# Install with performance optimizations
pip install "HelpingAI[mcp]" uvloop  # Faster event loop on Unix
```

### Validation Script

Use this script to validate your MCP installation:

```python
#!/usr/bin/env python3
"""MCP Installation Validation Script"""

def validate_mcp_installation():
    try:
        import mcp
        print(f"✅ MCP package installed: {mcp.__version__}")
    except ImportError as e:
        print(f"❌ MCP package not found: {e}")
        return False
    
    try:
        from HelpingAI.tools.mcp_manager import MCPManager
        print("✅ HelpingAI MCP integration available")
    except ImportError as e:
        print(f"❌ HelpingAI MCP integration not found: {e}")
        return False
    
    try:
        # Test basic MCP manager functionality
        manager = MCPManager()
        print("✅ MCP Manager initialized successfully")
    except Exception as e:
        print(f"❌ MCP Manager initialization failed: {e}")
        return False
    
    print("\n🎉 MCP installation validation successful!")
    return True

if __name__ == "__main__":
    validate_mcp_installation()
```

Save this as `validate_mcp.py` and run: `python validate_mcp.py`

## Configuring MCP Servers

MCP servers are configured within the `tools` parameter of your [`client.chat.completions.create()`](../HelpingAI/client/chat.py:1) call. The configuration is a Python list containing dictionaries, where one of these dictionaries must have the key `"mcpServers"`. The value associated with `"mcpServers"` is itself a dictionary, defining one or more MCP server instances.

Each entry within the `"mcpServers"` dictionary represents a single MCP server, identified by a user-defined `server_name` (e.g., `"time_server"`, `"remote_tool"`). The configuration for each server specifies how the SDK should connect to it.

The HelpingAI SDK provides **automatic lifecycle management** for MCP servers, including connection establishment, health monitoring, automatic reconnection, and graceful cleanup through the [`MCPManager`](../HelpingAI/tools/mcp_manager.py:21) singleton.

### Stdio Servers

Stdio (Standard Input/Output) servers are typically local command-line applications that communicate with the SDK via their standard I/O streams. This is the most common setup for running local tools or services and provides excellent performance for local operations.

**Configuration Parameters:**

-   `command` (str, required): The executable command to run the MCP server. This command must be accessible in your system's PATH or specified with its absolute path.
-   `args` (List[str], optional): A list of command-line arguments to pass to the `command`.
-   `env` (Dict[str, str], optional): A dictionary of environment variables to set for the server process.

**Basic Example:**

```python
tools_config_stdio = [
    {
        "mcpServers": {
            "time_server": {
                "command": "uvx",
                "args": ["mcp-server-time", "--local-timezone=America/New_York"],
                "env": {"DEBUG_MODE": "true"}
            },
            "file_system_server": {
                "command": "npx", # Example using npx for Node.js based MCP server
                "args": ["mcp-server-fs", "--root-dir=/tmp/my_data"]
            }
        }
    }
]
```

**Advanced Stdio Configuration:**

```python
tools_config_advanced_stdio = [
    {
        "mcpServers": {
            # Database integration server
            "database_server": {
                "command": "python",
                "args": ["-m", "mcp_database_server", "--config", "/path/to/db_config.json"],
                "env": {
                    "DATABASE_URL": "postgresql://user:pass@localhost:5432/mydb",
                    "DB_POOL_SIZE": "10",
                    "DB_TIMEOUT": "30",
                    "LOG_LEVEL": "INFO"
                }
            },
            # Development tools server
            "dev_tools": {
                "command": "/usr/local/bin/mcp-dev-server",
                "args": ["--workspace", "/home/user/projects", "--enable-git"],
                "env": {
                    "PATH": "/usr/local/bin:/usr/bin:/bin",
                    "GIT_AUTHOR_NAME": "AI Assistant",
                    "GIT_AUTHOR_EMAIL": "ai@example.com"
                }
            },
            # Custom Python server with virtual environment
            "custom_analytics": {
                "command": "/path/to/venv/bin/python",
                "args": ["-m", "custom_analytics_server", "--port", "8080"],
                "env": {
                    "PYTHONPATH": "/path/to/custom/modules",
                    "ANALYTICS_API_KEY": "your-api-key",
                    "CACHE_DIR": "/tmp/analytics_cache"
                }
            }
        }
    }
]
```

### HTTP (SSE and Streamable HTTP) Servers

HTTP-based MCP servers expose their functionalities over a network, typically using Server-Sent Events (SSE) or a custom streamable HTTP protocol. This is suitable for remote services, microservices, and distributed architectures.

**Configuration Parameters:**

-   `url` (str, required): The base URL of the MCP server endpoint.
-   `type` (Literal["sse", "streamable-http"], optional): The communication protocol type.
    -   `"sse"` (default): Uses Server-Sent Events for communication.
    -   `"streamable-http"`: Uses a custom streamable HTTP protocol, often for more efficient bidirectional communication.
-   `headers` (Dict[str, str], optional): A dictionary of HTTP headers to include in requests to the server (e.g., for authentication tokens).
-   `sse_read_timeout` (int, optional): For SSE connections, the timeout in seconds for reading data from the stream. Defaults to `300` seconds.

**Basic HTTP Example:**

```python
tools_config_http = [
    {
        "mcpServers": {
            "remote_tool_sse": {
                "url": "https://api.example.com/mcp/tools/sse",
                "type": "sse",
                "headers": {"Authorization": "Bearer your_sse_token"},
                "sse_read_timeout": 600
            },
            "remote_tool_streamable": {
                "url": "https://api.example.com/mcp/tools/stream",
                "type": "streamable-http",
                "headers": {"X-API-Key": "your_stream_api_key"}
            }
        }
    }
]
```

**Production HTTP Configuration:**

```python
import os

tools_config_production_http = [
    {
        "mcpServers": {
            # Enterprise API with full authentication
            "enterprise_api": {
                "url": "https://enterprise-mcp.company.com/api/v2/mcp",
                "type": "sse",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('ENTERPRISE_TOKEN')}",
                    "X-API-Version": "2.0",
                    "X-Client-ID": "helpingai-integration",
                    "Accept": "text/event-stream",
                    "User-Agent": "HelpingAI-SDK/1.0"
                },
                "sse_read_timeout": 900  # 15 minutes for long-running operations
            },
            # Microservice with custom authentication
            "analytics_service": {
                "url": "https://analytics.internal.company.com/mcp",
                "type": "streamable-http",
                "headers": {
                    "X-Service-Token": os.getenv('ANALYTICS_TOKEN'),
                    "X-Request-ID": "unique-request-id",
                    "Content-Type": "application/json"
                }
            },
            # Load-balanced service with health checks
            "distributed_compute": {
                "url": "https://compute-lb.company.com/mcp/v1",
                "type": "sse",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('COMPUTE_TOKEN')}",
                    "X-Health-Check": "enabled",
                    "X-Retry-Policy": "exponential"
                },
                "sse_read_timeout": 1800  # 30 minutes for compute-intensive tasks
            }
        }
    }
]
```

### Mixed Server Configuration

You can combine multiple server types in a single configuration for maximum flexibility:

```python
tools_config_mixed = [
    {
        "mcpServers": {
            # Local development tools
            "local_files": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "--root", "./workspace"]
            },
            # Remote API integration
            "external_api": {
                "url": "https://api.external-service.com/mcp",
                "type": "sse",
                "headers": {"Authorization": f"Bearer {os.getenv('EXTERNAL_TOKEN')}"}
            },
            # Database access
            "database": {
                "command": "python",
                "args": ["-m", "mcp_db_server"],
                "env": {"DATABASE_URL": os.getenv('DATABASE_URL')}
            },
            # Microservice
            "internal_service": {
                "url": "http://internal-service:8080/mcp",
                "type": "streamable-http"
            }
        }
    }
]
```

### Configuration Best Practices

#### Security Considerations

1. **Environment Variables for Secrets**:
   ```python
   import os
   
   tools_config_secure = [
       {
           "mcpServers": {
               "secure_api": {
                   "url": "https://api.example.com/mcp",
                   "headers": {
                       "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
                       "X-API-Key": os.getenv('API_KEY')
                   }
               }
           }
       }
   ]
   ```

2. **Validate Server Certificates**:
   ```python
   # Ensure HTTPS URLs for production
   tools_config_https = [
       {
           "mcpServers": {
               "production_api": {
                   "url": "https://secure-api.example.com/mcp",  # Always use HTTPS
                   "headers": {"Authorization": f"Bearer {os.getenv('PROD_TOKEN')}"}
               }
           }
       }
   ]
   ```

#### Performance Optimization

1. **Connection Timeouts**:
   ```python
   tools_config_optimized = [
       {
           "mcpServers": {
               "fast_service": {
                   "url": "https://fast-api.example.com/mcp",
                   "sse_read_timeout": 120  # Shorter timeout for fast services
               },
               "slow_service": {
                   "url": "https://slow-api.example.com/mcp",
                   "sse_read_timeout": 1800  # Longer timeout for slow operations
               }
           }
       }
   ]
   ```

2. **Resource Limits**:
   ```python
   tools_config_limited = [
       {
           "mcpServers": {
               "resource_intensive": {
                   "command": "python",
                   "args": ["-m", "heavy_mcp_server"],
                   "env": {
                       "MAX_MEMORY": "2GB",
                       "MAX_CPU_CORES": "4",
                       "PROCESS_TIMEOUT": "300"
                   }
               }
           }
       }
   ]
   ```

#### Reliability Patterns

1. **Health Check Configuration**:
   ```python
   tools_config_reliable = [
       {
           "mcpServers": {
               "monitored_service": {
                   "url": "https://api.example.com/mcp",
                   "headers": {
                       "X-Health-Check": "ping",
                       "X-Retry-Attempts": "3",
                       "X-Backoff-Strategy": "exponential"
                   }
               }
           }
       }
   ]
   ```

2. **Fallback Servers**:
   ```python
   # Configure primary and backup servers
   tools_config_fallback = [
       {
           "mcpServers": {
               "primary_service": {
                   "url": "https://primary-api.example.com/mcp",
                   "headers": {"Authorization": f"Bearer {os.getenv('PRIMARY_TOKEN')}"}
               },
               "backup_service": {
                   "url": "https://backup-api.example.com/mcp",
                   "headers": {"Authorization": f"Bearer {os.getenv('BACKUP_TOKEN')}"}
               }
           }
       }
   ]
   ```

### Configuration Validation

The SDK automatically validates MCP server configurations and provides helpful error messages:

```python
from HelpingAI.tools.mcp_manager import MCPManager

# Test configuration validity
manager = MCPManager()
config = {"mcpServers": {"test": {"command": "echo", "args": ["hello"]}}}

if manager.is_valid_mcp_servers_config(config):
    print("✅ Configuration is valid")
else:
    print("❌ Configuration is invalid")
```

### Environment-Specific Configurations

#### Development Environment

```python
dev_tools = [
    {
        "mcpServers": {
            "local_dev": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "--root", "./dev-workspace"],
                "env": {"LOG_LEVEL": "DEBUG"}
            }
        }
    }
]
```

#### Staging Environment

```python
staging_tools = [
    {
        "mcpServers": {
            "staging_api": {
                "url": "https://staging-api.example.com/mcp",
                "headers": {"Authorization": f"Bearer {os.getenv('STAGING_TOKEN')}"},
                "sse_read_timeout": 600
            }
        }
    }
]
```

#### Production Environment

```python
production_tools = [
    {
        "mcpServers": {
            "prod_api": {
                "url": "https://api.example.com/mcp",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('PROD_TOKEN')}",
                    "X-Environment": "production",
                    "X-Client-Version": "1.0.0"
                },
                "sse_read_timeout": 1200
            }
        }
    }
]
```

## Using MCP Tools

Once MCP servers are configured, the tools they expose become available to your AI model just like any other tool defined using the [`@tools`](../HelpingAI/tools/core.py:1) decorator or [`Fn`](../HelpingAI/tools/core.py:1) class. The SDK automatically handles the underlying communication with the MCP server through the [`MCPManager`](../HelpingAI/tools/mcp_manager.py:21), abstracting away the complexities of the protocol.

### Key Features

- **Automatic Lifecycle Management**: MCP servers are automatically initialized, monitored, and cleaned up
- **Seamless Integration**: MCP tools work transparently with built-in tools like [`code_interpreter`](../HelpingAI/tools/builtin_tools/code_interpreter.py:1) and [`web_search`](../HelpingAI/tools/builtin_tools/web_search.py:1)
- **Enhanced Workflow Integration**: MCP tools benefit from automatic tool caching and the enhanced workflow system
- **Automatic Reconnection**: The SDK handles connection failures and automatically reconnects to MCP servers
- **Resource Discovery**: Automatic discovery and access to MCP server resources

### MCP Tool Naming Convention

Tools provided by MCP servers follow a specific naming convention within the HelpingAI SDK:

`{server_name}-{tool_name}`

-   `{server_name}`: This is the name you assigned to the MCP server in your configuration (e.g., `"time_server"`, `"remote_tool_sse"`).
-   `{tool_name}`: This is the actual name of the tool as advertised by the MCP server itself (e.g., `"now"`, `"fetch_data"`).

For example, if you configure a `time_server` that exposes a tool named `now`, the SDK will make it available as `time_server-now`.

### Integration with Built-in Tools

MCP tools work seamlessly alongside built-in tools, creating powerful mixed workflows:

```python
from HelpingAI import HAI

client = HAI()

# Mixed tools configuration: MCP + built-in tools
tools = [
    # MCP server for file operations
    {
        "mcpServers": {
            "filesystem": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "--root", "./workspace"]
            }
        }
    },
    # Built-in tools
    "code_interpreter",  # For code execution
    "web_search"         # For web searches
]

# The AI can now use file operations, code execution, and web search together
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{
        "role": "user",
        "content": "Search for Python best practices, save them to a file, and create a summary script"
    }],
    tools=tools
)
```

### Enhanced Workflow Integration

MCP tools benefit from the enhanced workflow system with automatic tool caching and intelligent execution:

```python
from HelpingAI import HAI

client = HAI()

# Configure MCP tools with automatic caching
tools = [
    {
        "mcpServers": {
            "database": {
                "command": "python",
                "args": ["-m", "mcp_db_server"],
                "env": {"DATABASE_URL": "postgresql://localhost/myapp"}
            },
            "analytics": {
                "url": "https://analytics-api.company.com/mcp",
                "headers": {"Authorization": "Bearer token"}
            }
        }
    }
]

# The SDK automatically caches tool results and optimizes execution
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{
        "role": "user",
        "content": "Get user data from database and generate analytics report"
    }],
    tools=tools
)
```

### Helper Methods for Tool Execution

The SDK provides helper methods for executing tool calls efficiently:

```python
from HelpingAI import HAI

client = HAI()

# Configure tools
tools = [
    {
        "mcpServers": {
            "time_server": {
                "command": "uvx",
                "args": ["mcp-server-time"]
            }
        }
    }
]

# Method 1: Using execute_tool_calls helper
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "What time is it?"}],
    tools=tools
)

if response.choices[0].message.tool_calls:
    # Execute all tool calls automatically
    tool_results = client.execute_tool_calls(
        response.choices[0].message.tool_calls,
        tools
    )
    
    # Continue conversation with results
    messages = [
        {"role": "user", "content": "What time is it?"},
        response.choices[0].message,
        *tool_results
    ]
    
    final_response = client.chat.completions.create(
        model="HelpingAI2.5-10B",
        messages=messages,
        tools=tools
    )
```

### Real-World Mixed Tool Workflow

Here's a comprehensive example showing MCP tools working with built-in tools:

```python
from HelpingAI import HAI
import json

client = HAI()

# Production-ready mixed tools configuration
tools = [
    # MCP servers for specialized tasks
    {
        "mcpServers": {
            # File system operations
            "filesystem": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "--root", "./project"]
            },
            # Database operations
            "database": {
                "command": "python",
                "args": ["-m", "database_mcp_server"],
                "env": {
                    "DATABASE_URL": "postgresql://user:pass@localhost/db",
                    "QUERY_TIMEOUT": "30"
                }
            },
            # External API integration
            "external_api": {
                "url": "https://api.external-service.com/mcp",
                "type": "sse",
                "headers": {"Authorization": "Bearer api-token"},
                "sse_read_timeout": 300
            }
        }
    },
    # Built-in tools
    "code_interpreter",  # For data processing and analysis
    "web_search"         # For research and information gathering
]

# Complex workflow: research -> data processing -> file operations -> analysis
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{
        "role": "user",
        "content": """
        Research recent trends in AI development, fetch our internal project data,
        analyze the trends against our data, and create a comprehensive report
        saved to our project directory.
        """
    }],
    tools=tools
)

# The AI can now:
# 1. Use web_search to research AI trends
# 2. Use database MCP server to fetch internal data
# 3. Use code_interpreter to analyze and compare data
# 4. Use external_api MCP server for additional insights
# 5. Use filesystem MCP server to save the report
```

### Direct Tool Calling

You can also call MCP tools directly using [`client.call()`](../HelpingAI/client/main.py:1):

```python
from HelpingAI import HAI

client = HAI()

# Configure tools first
tools = [
    {
        "mcpServers": {
            "time_server": {
                "command": "uvx",
                "args": ["mcp-server-time"]
            }
        }
    }
]

# Configure the tools in the client
client.configure_tools(tools)

# Direct tool calling
result = client.call("time_server-now", {})
print(f"Current time: {result}")

# Call with parameters
result = client.call("time_server-now", {"timezone": "UTC"})
print(f"UTC time: {result}")
```

### Error Handling Patterns

Comprehensive error handling for MCP tools:

```python
from HelpingAI import HAI
from HelpingAI.tools.errors import ToolExecutionError
from HelpingAI.error import HAIError
import json

client = HAI()

tools = [
    {
        "mcpServers": {
            "api_server": {
                "url": "https://api.example.com/mcp",
                "headers": {"Authorization": "Bearer token"}
            }
        }
    }
]

def handle_mcp_tool_calls(tool_calls, tools):
    """Handle MCP tool calls with comprehensive error handling."""
    tool_results = []
    
    for tool_call in tool_calls:
        try:
            # Parse arguments
            args = json.loads(tool_call.function.arguments)
            
            # Execute tool with retry logic
            result = client.call(tool_call.function.name, args)
            
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": str(result)
            })
            
        except json.JSONDecodeError as e:
            # Handle invalid JSON arguments
            error_msg = f"Invalid JSON arguments: {e}"
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": f"Error: {error_msg}"
            })
            
        except ToolExecutionError as e:
            # Handle MCP tool execution errors
            error_msg = f"Tool execution failed: {e}"
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": f"Error: {error_msg}"
            })
            
        except HAIError as e:
            # Handle general SDK errors
            error_msg = f"SDK error: {e}"
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": f"Error: {error_msg}"
            })
            
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Unexpected error: {e}"
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": f"Error: {error_msg}"
            })
    
    return tool_results

# Usage with error handling
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Call the API server"}],
    tools=tools
)

if response.choices[0].message.tool_calls:
    tool_results = handle_mcp_tool_calls(
        response.choices[0].message.tool_calls,
        tools
    )
    # Continue with tool results...
```

### Performance Optimization

Optimize MCP tool usage for production environments:

```python
from HelpingAI import HAI
import asyncio
from concurrent.futures import ThreadPoolExecutor

client = HAI()

# Configure tools with performance optimizations
tools = [
    {
        "mcpServers": {
            # Fast local server
            "local_cache": {
                "command": "uvx",
                "args": ["mcp-cache-server", "--memory-limit", "1GB"]
            },
            # Remote server with optimized timeouts
            "remote_api": {
                "url": "https://fast-api.example.com/mcp",
                "sse_read_timeout": 60,  # Shorter timeout for fast API
                "headers": {
                    "Connection": "keep-alive",
                    "Keep-Alive": "timeout=30"
                }
            }
        }
    }
]

# Use connection pooling and caching for better performance
def optimized_tool_execution():
    # Configure tools once
    client.configure_tools(tools)
    
    # Batch multiple tool calls for efficiency
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(client.call, "local_cache-get", {"key": f"item_{i}"})
            for i in range(10)
        ]
        results = [future.result() for future in futures]
    
    return results
```

## Advanced MCP Usage

### MCP Server Lifecycle Management

The [`MCPManager`](../HelpingAI/tools/mcp_manager.py:21) provides sophisticated lifecycle management:

```python
from HelpingAI.tools.mcp_manager import MCPManager

# Access the singleton manager
manager = MCPManager()

# Check server health
def check_mcp_health():
    """Check the health of all MCP connections."""
    healthy_servers = []
    failed_servers = []
    
    for client_id, client in manager.clients.items():
        try:
            # Test connection with ping
            asyncio.run(client.session.send_ping())
            healthy_servers.append(client_id)
        except Exception as e:
            failed_servers.append((client_id, str(e)))
    
    return {
        "healthy": healthy_servers,
        "failed": failed_servers,
        "total": len(manager.clients)
    }

# Manual cleanup if needed
def cleanup_mcp_resources():
    """Manually cleanup MCP resources."""
    manager.shutdown()
```

### Custom MCP Tool Creation

Create custom tools that wrap MCP functionality:

```python
from HelpingAI.tools import tools
from HelpingAI import HAI

client = HAI()

@tools
def enhanced_file_search(query: str, file_type: str = "all") -> str:
    """Enhanced file search using MCP filesystem server with additional processing."""
    
    # Configure MCP server if not already done
    mcp_tools = [{
        "mcpServers": {
            "filesystem": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "--root", "./workspace"]
            }
        }
    }]
    
    client.configure_tools(mcp_tools)
    
    # Use MCP tool for basic search
    search_result = client.call("filesystem-search", {
        "query": query,
        "type": file_type
    })
    
    # Add custom processing
    processed_result = f"Enhanced search results for '{query}':\n{search_result}"
    
    return processed_result

# Use the enhanced tool
tools_config = [enhanced_file_search]

response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Search for Python files containing 'async'"}],
    tools=tools_config
)
```

### Multi-Server Coordination

Coordinate multiple MCP servers for complex workflows:

```python
from HelpingAI import HAI

client = HAI()

# Configure multiple specialized servers
tools = [
    {
        "mcpServers": {
            # Data processing server
            "data_processor": {
                "command": "python",
                "args": ["-m", "data_mcp_server"]
            },
            # Visualization server
            "visualizer": {
                "command": "uvx",
                "args": ["mcp-chart-server"]
            },
            # Report generator
            "reporter": {
                "url": "https://reports.company.com/mcp",
                "headers": {"Authorization": "Bearer report-token"}
            },
            # File storage
            "storage": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "--root", "./reports"]
            }
        }
    }
]

# Orchestrated workflow
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{
        "role": "user",
        "content": """
        Process the sales data, create visualizations, generate a comprehensive
        report, and save everything to the reports directory.
        """
    }],
    tools=tools
)

# The AI will coordinate:
# 1. data_processor - Process raw sales data
# 2. visualizer - Create charts and graphs
# 3. reporter - Generate formatted report
# 4. storage - Save all files to reports directory
```

## MCP Resources

MCP servers can provide access to data sources called resources. These represent structured data that can be used as context for AI operations. The SDK automatically creates tools for listing and reading these resources through the [`MCPClient`](../HelpingAI/tools/mcp_client.py:19) implementation.

### Automatic Resource Discovery

When an MCP server provides resources, the SDK automatically creates two tools:

- `{server_name}-list_resources`: Lists available resources with metadata
- `{server_name}-read_resource`: Reads a specific resource by its URI

### Basic Resource Usage

```python
from HelpingAI import HAI

client = HAI()

# Configure MCP server with resources
tools = [
    {
        "mcpServers": {
            "document_server": {
                "command": "uvx",
                "args": ["mcp-server-documents", "--root", "./docs"]
            }
        }
    }
]

client.configure_tools(tools)

# List available resources
resources = client.call("document_server-list_resources", {})
print("Available resources:", resources)

# Read a specific resource
content = client.call("document_server-read_resource", {"uri": "file://./docs/readme.md"})
print("Resource content:", content)
```

### Advanced Resource Integration

Resources can be used as context for AI operations:

```python
from HelpingAI import HAI

client = HAI()

tools = [
    {
        "mcpServers": {
            "knowledge_base": {
                "url": "https://kb.company.com/mcp",
                "headers": {"Authorization": "Bearer kb-token"}
            }
        }
    }
]

# AI workflow using resources as context
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{
        "role": "user",
        "content": """
        List the available knowledge base resources, read the company policies,
        and answer: What is our remote work policy?
        """
    }],
    tools=tools
)

# The AI will:
# 1. Call knowledge_base-list_resources to see what's available
# 2. Call knowledge_base-read_resource to read policy documents
# 3. Analyze the content and provide an answer
```

### Resource-Driven Workflows

Use resources to drive complex AI workflows:

```python
from HelpingAI import HAI

client = HAI()

# Multiple servers with different resource types
tools = [
    {
        "mcpServers": {
            # Code repository server
            "codebase": {
                "command": "uvx",
                "args": ["mcp-server-git", "--repo", "./my-project"]
            },
            # Documentation server
            "docs": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "--root", "./documentation"]
            },
            # API specification server
            "api_specs": {
                "url": "https://api-docs.company.com/mcp",
                "headers": {"Authorization": "Bearer docs-token"}
            }
        }
    }
]

# Comprehensive analysis using multiple resource types
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{
        "role": "user",
        "content": """
        Analyze our codebase structure, review the documentation, check API
        specifications, and create a comprehensive project overview report.
        """
    }],
    tools=tools
)
```

### Resource Metadata and Filtering

Resources include metadata that can be used for filtering and organization:

```python
from HelpingAI import HAI
import json

client = HAI()

tools = [
    {
        "mcpServers": {
            "content_server": {
                "command": "python",
                "args": ["-m", "content_mcp_server"],
                "env": {"CONTENT_DIR": "./content"}
            }
        }
    }
]

client.configure_tools(tools)

# Get resources with metadata
resources_raw = client.call("content_server-list_resources", {})
resources = json.loads(resources_raw)

# Filter resources by type
markdown_resources = [
    r for r in resources
    if r.get('mimeType') == 'text/markdown'
]

# Read multiple related resources
for resource in markdown_resources[:5]:  # Read first 5 markdown files
    content = client.call("content_server-read_resource", {"uri": resource['uri']})
    print(f"Resource: {resource['name']}")
    print(f"Content preview: {content[:200]}...")
```

## Security Considerations

### Authentication and Authorization

Secure your MCP integrations with proper authentication:

```python
import os
from HelpingAI import HAI

# Use environment variables for sensitive data
tools = [
    {
        "mcpServers": {
            "secure_api": {
                "url": "https://secure-api.company.com/mcp",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('SECURE_API_TOKEN')}",
                    "X-Client-ID": os.getenv('CLIENT_ID'),
                    "X-Client-Secret": os.getenv('CLIENT_SECRET')
                }
            }
        }
    }
]

# Validate environment variables
required_vars = ['SECURE_API_TOKEN', 'CLIENT_ID', 'CLIENT_SECRET']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")
```

### Network Security

Configure secure connections for production:

```python
# Production security configuration
production_tools = [
    {
        "mcpServers": {
            "production_api": {
                "url": "https://api.company.com/mcp",  # Always use HTTPS
                "headers": {
                    "Authorization": f"Bearer {os.getenv('PROD_TOKEN')}",
                    "X-API-Version": "v2",
                    "User-Agent": "HelpingAI-SDK/1.0",
                    "Accept": "application/json"
                },
                "sse_read_timeout": 300
            }
        }
    }
]

# Certificate validation is handled automatically
# For custom certificates, configure your environment appropriately
```

### Access Control

Implement access control for MCP tools:

```python
from HelpingAI import HAI
from functools import wraps

def require_permission(permission):
    """Decorator to check permissions before MCP tool execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check user permissions (implement your logic)
            if not user_has_permission(permission):
                raise PermissionError(f"Permission required: {permission}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@require_permission("database_access")
def secure_database_query(query: str):
    """Secure database query with permission checking."""
    client = HAI()
    tools = [{
        "mcpServers": {
            "database": {
                "command": "python",
                "args": ["-m", "secure_db_mcp"],
                "env": {"DATABASE_URL": os.getenv('SECURE_DB_URL')}
            }
        }
    }]
    
    client.configure_tools(tools)
    return client.call("database-query", {"sql": query})
```

## Troubleshooting

### Common MCP Issues and Solutions

#### Connection Failures

```python
from HelpingAI.tools.mcp_manager import MCPManager
from HelpingAI.error import HAIError

def diagnose_mcp_connection(server_config):
    """Diagnose MCP connection issues."""
    manager = MCPManager()
    
    try:
        # Test configuration validity
        if not manager.is_valid_mcp_servers_config({"mcpServers": {"test": server_config}}):
            return "Invalid server configuration"
        
        # Test connection
        test_config = {"mcpServers": {"test_server": server_config}}
        tools = manager.init_config(test_config)
        
        return f"Connection successful. Available tools: {len(tools)}"
        
    except ImportError as e:
        return f"MCP package not available: {e}"
    except HAIError as e:
        return f"Connection failed: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

# Test server configuration
stdio_config = {
    "command": "uvx",
    "args": ["mcp-server-time"]
}

http_config = {
    "url": "https://api.example.com/mcp",
    "headers": {"Authorization": "Bearer token"}
}

print("Stdio server:", diagnose_mcp_connection(stdio_config))
print("HTTP server:", diagnose_mcp_connection(http_config))
```

#### Performance Issues

```python
import time
from HelpingAI import HAI

def benchmark_mcp_performance():
    """Benchmark MCP tool performance."""
    client = HAI()
    
    tools = [
        {
            "mcpServers": {
                "test_server": {
                    "command": "uvx",
                    "args": ["mcp-server-time"]
                }
            }
        }
    ]
    
    client.configure_tools(tools)
    
    # Benchmark tool calls
    times = []
    for i in range(10):
        start = time.time()
        result = client.call("test_server-now", {})
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    print(f"Average call time: {avg_time:.3f}s")
    print(f"Min: {min(times):.3f}s, Max: {max(times):.3f}s")
    
    return avg_time

# Run performance benchmark
benchmark_mcp_performance()
```

#### Debug Mode

Enable debug mode for detailed MCP logging:

```python
import logging
from HelpingAI import HAI

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('HelpingAI.tools.mcp')

client = HAI()

# Configure with debug environment
tools = [
    {
        "mcpServers": {
            "debug_server": {
                "command": "uvx",
                "args": ["mcp-server-time"],
                "env": {
                    "DEBUG": "true",
                    "LOG_LEVEL": "DEBUG"
                }
            }
        }
    }
]

# Debug information will be logged
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "What time is it?"}],
    tools=tools
)
```

## Error Handling

The SDK provides comprehensive error handling for MCP operations through the [`MCPManager`](../HelpingAI/tools/mcp_manager.py:21) and [`MCPClient`](../HelpingAI/tools/mcp_client.py:19) classes.

### Error Types

1. **Import Errors**: When MCP package is not installed
2. **Configuration Errors**: Invalid server configurations
3. **Connection Errors**: Network or server connection failures
4. **Tool Execution Errors**: Errors during tool execution
5. **Resource Errors**: Issues accessing MCP resources

### Comprehensive Error Handling

```python
from HelpingAI import HAI
from HelpingAI.tools.errors import ToolExecutionError, ToolRegistrationError
from HelpingAI.error import HAIError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_mcp_execution():
    """Example of robust MCP tool execution with comprehensive error handling."""
    client = HAI()
    
    tools = [
        {
            "mcpServers": {
                "api_server": {
                    "url": "https://api.example.com/mcp",
                    "headers": {"Authorization": "Bearer token"},
                    "sse_read_timeout": 30
                }
            }
        }
    ]
    
    try:
        # Configure tools with validation
        client.configure_tools(tools)
        logger.info("MCP tools configured successfully")
        
        # Execute with error handling
        response = client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[{"role": "user", "content": "Call the API server"}],
            tools=tools
        )
        
        return response
        
    except ImportError as e:
        logger.error(f"MCP package not available: {e}")
        # Fallback to non-MCP tools
        return client.chat.completions.create(
            model="HelpingAI2.5-10B",
            messages=[{"role": "user", "content": "Process without external tools"}]
        )
        
    except ToolRegistrationError as e:
        logger.error(f"Tool registration failed: {e}")
        # Handle registration failure
        raise
        
    except HAIError as e:
        logger.error(f"SDK error: {e}")
        # Handle SDK-specific errors
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Handle unexpected errors
        raise

# Usage
try:
    result = robust_mcp_execution()
    print("Success:", result.choices[0].message.content)
except Exception as e:
    print(f"Failed: {e}")
```

### Retry Logic

Implement retry logic for transient failures:

```python
import time
import random
from functools import wraps
from HelpingAI.tools.errors import ToolExecutionError
from HelpingAI.error import HAIError

def retry_on_failure(max_retries=3, backoff_factor=1.0):
    """Retry decorator for MCP operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (HAIError, ToolExecutionError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        delay = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                        continue
                    break
            
            raise last_exception
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, backoff_factor=0.5)
def resilient_mcp_call(client, tool_name, args):
    """Make a resilient MCP tool call with retry logic."""
    return client.call(tool_name, args)

# Usage
client = HAI()
# Configure tools...
result = resilient_mcp_call(client, "api_server-fetch", {"url": "https://example.com"})
```

## Production Deployment

### Best Practices for Production

1. **Environment Configuration**:
   ```python
   import os
   from HelpingAI import HAI
   
   # Production environment setup
   def get_production_tools():
       return [
           {
               "mcpServers": {
                   "production_db": {
                       "command": "python",
                       "args": ["-m", "production_db_mcp"],
                       "env": {
                           "DATABASE_URL": os.getenv('PROD_DATABASE_URL'),
                           "POOL_SIZE": "20",
                           "TIMEOUT": "30"
                       }
                   },
                   "cache_service": {
                       "url": "https://cache.prod.company.com/mcp",
                       "headers": {
                           "Authorization": f"Bearer {os.getenv('CACHE_TOKEN')}",
                           "X-Environment": "production"
                       },
                       "sse_read_timeout": 300
                   }
               }
           }
       ]
   ```

2. **Health Monitoring**:
   ```python
   from HelpingAI.tools.mcp_manager import MCPManager
   import asyncio
   
   async def health_check():
       """Production health check for MCP services."""
       manager = MCPManager()
       health_status = {
           "healthy": [],
           "unhealthy": [],
           "total_servers": len(manager.clients)
       }
       
       for client_id, client in manager.clients.items():
           try:
               await client.session.send_ping()
               health_status["healthy"].append(client_id)
           except Exception as e:
               health_status["unhealthy"].append({
                   "client_id": client_id,
                   "error": str(e)
               })
       
       return health_status
   ```

3. **Performance Monitoring**:
   ```python
   import time
   from contextlib import contextmanager
   
   @contextmanager
   def measure_mcp_performance(operation_name):
       """Context manager for measuring MCP operation performance."""
       start_time = time.time()
       try:
           yield
       finally:
           duration = time.time() - start_time
           # Log to your monitoring system
           print(f"MCP operation '{operation_name}' took {duration:.3f}s")
   
   # Usage
   with measure_mcp_performance("database_query"):
       result = client.call("production_db-query", {"sql": "SELECT COUNT(*) FROM users"})
   ```

### Scaling Considerations

For high-traffic applications, consider these scaling patterns:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from HelpingAI import HAI

class ScalableMCPClient:
    """Scalable MCP client with connection pooling."""
    
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def batch_execute(self, tool_calls):
        """Execute multiple MCP tool calls in parallel."""
        client = HAI()
        # Configure tools once
        
        futures = []
        for tool_name, args in tool_calls:
            future = self.executor.submit(client.call, tool_name, args)
            futures.append((tool_name, future))
        
        results = {}
        for tool_name, future in futures:
            try:
                results[tool_name] = future.result(timeout=30)
            except Exception as e:
                results[tool_name] = f"Error: {e}"
        
        return results

# Usage for high-throughput scenarios
scalable_client = ScalableMCPClient(max_workers=20)
batch_calls = [
    ("api_server-fetch", {"url": f"https://api.example.com/data/{i}"})
    for i in range(100)
]
results = scalable_client.batch_execute(batch_calls)
```

## Conclusion

The Model Context Protocol (MCP) integration in HelpingAI SDK provides a powerful and flexible way to extend your AI applications with external tools and services. Through the sophisticated [`MCPManager`](../HelpingAI/tools/mcp_manager.py:21) and [`MCPClient`](../HelpingAI/tools/mcp_client.py:19) implementations, you get:

### Key Advantages

- **Automatic Lifecycle Management**: No manual connection handling required
- **Seamless Integration**: MCP tools work transparently with built-in tools
- **Enhanced Workflow Support**: Automatic caching and intelligent execution
- **Production Ready**: Comprehensive error handling, monitoring, and scaling support
- **Security First**: Built-in authentication, authorization, and secure communication
- **Resource Discovery**: Automatic access to MCP server resources and data sources

### Getting Started Checklist

1. **Install MCP Support**: `pip install "HelpingAI[mcp]"`
2. **Configure Your First Server**: Start with a simple stdio server
3. **Test Integration**: Use the validation script provided
4. **Explore Mixed Workflows**: Combine MCP tools with built-in tools
5. **Implement Error Handling**: Add robust error handling for production
6. **Monitor Performance**: Use the provided monitoring tools
7. **Scale as Needed**: Implement batch processing and connection pooling

### Next Steps

- **Explore MCP Ecosystem**: Check out available MCP servers for your use case
- **Build Custom Servers**: Create specialized MCP servers for your domain
- **Contribute**: Share your MCP integrations with the community
- **Monitor and Optimize**: Use the provided tools to optimize performance

### Community and Support

- **Documentation**: This guide and the [API Reference](./api_reference.md)
- **Examples**: Check the [`examples/`](../examples/) directory for more use cases
- **Issues**: Report issues on the HelpingAI GitHub repository
- **Discussions**: Join community discussions about MCP integrations

The MCP integration transforms HelpingAI from a powerful AI SDK into a comprehensive platform for building sophisticated, tool-augmented AI applications. Start with simple integrations and gradually build more complex workflows as your needs evolve.

## Additional Resources

### Official MCP Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)

### HelpingAI Documentation

- [Getting Started Guide](./getting_started.md)
- [Tool Calling Documentation](./tool_calling.md)
- [API Reference](./api_reference.md)
- [Examples and Use Cases](./examples.md)

### Community MCP Servers

Popular MCP servers you can use with HelpingAI:

- **File System**: `mcp-server-filesystem` - File operations and management
- **Database**: `mcp-server-postgres` - PostgreSQL database integration
- **Git**: `mcp-server-git` - Git repository operations
- **Web**: `mcp-server-fetch` - HTTP requests and web scraping
- **Time**: `mcp-server-time` - Time and date operations
- **Memory**: `mcp-server-memory` - Persistent memory for AI conversations

### Development Tools

- **MCP Inspector**: Debug and inspect MCP server communications
- **MCP Test Suite**: Validate your MCP server implementations
- **Performance Profiler**: Monitor MCP tool execution performance

### Best Practices Repository

Find additional examples and patterns:

```bash
# Clone the HelpingAI examples repository
git clone https://github.com/HelpingAI/mcp-examples.git
cd mcp-examples

# Explore different integration patterns
ls patterns/
# - basic-integration/
# - mixed-workflows/
# - production-deployment/
# - custom-servers/
# - security-patterns/
```

### Contributing

Help improve MCP integration:

1. **Report Issues**: Found a bug? Report it on GitHub
2. **Submit Examples**: Share your integration patterns
3. **Write Servers**: Create new MCP servers for the community
4. **Improve Documentation**: Help make this guide even better

---

*This documentation is part of the HelpingAI Python SDK. For the latest updates and community discussions, visit our [GitHub repository](https://github.com/HelpingAI/HelpingAI-python).*