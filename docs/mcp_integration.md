# MCP Integration Guide

This guide explains how to integrate external tools and services using MCP (Model Context Protocol) servers with the HelpingAI Python SDK.

## What is MCP?

The **Model Context Protocol (MCP)** is a standardized communication protocol that enables the HelpingAI SDK to interact seamlessly with external tool servers. By integrating MCP servers, you can significantly extend the capabilities of your AI models, allowing them to access and utilize a diverse range of external tools, services, and data sources beyond their inherent knowledge.

MCP facilitates a clear separation of concerns: your AI model focuses on reasoning and decision-making, while specialized MCP servers handle the execution of specific tasks (e.g., fetching real-time data, running code, interacting with external APIs). This modular approach enhances the flexibility, scalability, and maintainability of AI-powered applications.

## Installation

To leverage the full capabilities of MCP integration, you need to install the `mcp` Python package. This package provides the necessary client-side components to communicate with MCP servers.

### Recommended Installation

The easiest way to install `mcp` along with the HelpingAI SDK is by specifying the `mcp` extra during installation:

```bash
pip install "HelpingAI[mcp]"
```

This command ensures that all required dependencies for MCP functionality are installed automatically.

### Manual Installation

If you prefer to install `mcp` separately, you can do so using pip:

```bash
pip install -U mcp
```

### Verifying Installation

After installation, you can verify that the `mcp` package is correctly installed by running a simple Python command:

```bash
python -c "import mcp; print(mcp.__version__)"
```

If the installation was successful, this command should print the installed version of the `mcp` package.

### Common Installation Issues

-   **`ImportError: Could not import mcp`**: This error indicates that the `mcp` package is not installed or not accessible in your Python environment. Ensure you have run the `pip install` command correctly.
-   **Dependency Conflicts**: If you encounter dependency conflicts, consider using a virtual environment to isolate your project dependencies.

For more advanced troubleshooting or specific environment setups, refer to the official `mcp` package documentation.

## Configuring MCP Servers

MCP servers are configured within the `tools` parameter of your `client.chat.completions.create()` call. The configuration is a Python list containing dictionaries, where one of these dictionaries must have the key `"mcpServers"`. The value associated with `"mcpServers"` is itself a dictionary, defining one or more MCP server instances.

Each entry within the `"mcpServers"` dictionary represents a single MCP server, identified by a user-defined `server_name` (e.g., `"time_server"`, `"remote_tool"`). The configuration for each server specifies how the SDK should connect to it.

### Stdio Servers

Stdio (Standard Input/Output) servers are typically local command-line applications that communicate with the SDK via their standard I/O streams. This is a common setup for running local tools or services.

**Configuration Parameters:**

-   `command` (str, required): The executable command to run the MCP server. This command must be accessible in your system's PATH or specified with its absolute path.
-   `args` (List[str], optional): A list of command-line arguments to pass to the `command`.
-   `env` (Dict[str, str], optional): A dictionary of environment variables to set for the server process.

**Example:**

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

# Pass this configuration to the chat completions create method
# response = client.chat.completions.create(
#     model="Dhanishtha-2.0-preview",
#     messages=[{"role": "user", "content": "What time is it in New York?"}],
#     tools=tools_config_stdio
# )
```

### HTTP (SSE and Streamable HTTP) Servers

HTTP-based MCP servers expose their functionalities over a network, typically using Server-Sent Events (SSE) or a custom streamable HTTP protocol. This is suitable for remote services or microservices.

**Configuration Parameters:**

-   `url` (str, required): The base URL of the MCP server endpoint.
-   `type` (Literal["sse", "streamable-http"], optional): The communication protocol type.
    -   `"sse"` (default): Uses Server-Sent Events for communication.
    -   `"streamable-http"`: Uses a custom streamable HTTP protocol, often for more efficient bidirectional communication.
-   `headers` (Dict[str, str], optional): A dictionary of HTTP headers to include in requests to the server (e.g., for authentication tokens).
-   `sse_read_timeout` (int, optional): For SSE connections, the timeout in seconds for reading data from the stream. Defaults to `300` seconds.

**Example:**

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

# Pass this configuration to the chat completions create method
# response = client.chat.completions.create(
#     model="Dhanishtha-2.0-preview",
#     messages=[{"role": "user", "content": "Fetch data from the remote tool."}],
#     tools=tools_config_http
# )
```

## Using MCP Tools

Once MCP servers are configured, the tools they expose become available to your AI model just like any other tool defined using the `@tools` decorator or `Fn` class. The SDK automatically handles the underlying communication with the MCP server, abstracting away the complexities of the protocol.

### MCP Tool Naming Convention

Tools provided by MCP servers follow a specific naming convention within the HelpingAI SDK:

`{server_name}-{tool_name}`

-   `{server_name}`: This is the name you assigned to the MCP server in your configuration (e.g., `"time_server"`, `"remote_tool_sse"`).
-   `{tool_name}`: This is the actual name of the tool as advertised by the MCP server itself (e.g., `"now"`, `"fetch_data"`).

For example, if you configure a `time_server` that exposes a tool named `now`, the SDK will make it available as `time_server-now`.

### Example: Using an MCP Tool in Chat Completions

This example demonstrates how to use an MCP tool (assuming a `time_server` is configured to provide a `now` tool) within a chat completion and handle its execution.

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools # To get tools defined with @tools or Fn
import json

client = HAI()

# 1. Define your MCP server configuration
mcp_tools_config = [
    {
        "mcpServers": {
            "time_server": {
                "command": "uvx", # Assuming uvx and mcp-server-time are installed
                "args": ["mcp-server-time"]
            }
        }
    }
]

# 2. Combine with any other tools you might have
# For this example, we'll just use the MCP tools
all_tools_for_model = mcp_tools_config # Or get_tools() + mcp_tools_config

# 3. Make a chat completion request, including the MCP tools
messages = [
    {"role": "user", "content": "What is the current time?"}
]

print("\n--- Initial Chat Completion Request ---")
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=all_tools_for_model,
    tool_choice="auto"
)

message = response.choices[0].message

# 4. Handle the model's response (check for tool calls)
if message.tool_calls:
    print("\n--- Model wants to call tools ---")
    tool_messages_for_follow_up = []

    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        function_args_str = tool_call.function.arguments
        
        print(f"Model called tool: {function_name} with arguments: {function_args_str}")

        try:
            # Parse arguments (MCP tools typically expect JSON arguments)
            function_args = json.loads(function_args_str)
            
            # Execute the MCP tool using client.call()
            # The client automatically routes the call to the correct MCP server
            tool_result = client.call(function_name, function_args)
            
            print(f"Tool execution result: {tool_result}")
            
            # Create a tool response message to send back to the model
            tool_messages_for_follow_up.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(tool_result) # Tool output should be a string
            })

        except json.JSONDecodeError:
            error_content = f"Error: Invalid JSON arguments for tool {function_name}: {function_args_str}"
            print(error_content)
            tool_messages_for_follow_up.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": error_content
            })
        except Exception as e:
            error_content = f"Error executing MCP tool {function_name}: {e}"
            print(error_content)
            tool_messages_for_follow_up.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": error_content
            })

    # 5. Continue the conversation with the tool results
    print("\n--- Continuing Chat with Tool Results ---")
    follow_up_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages + [message] + tool_messages_for_follow_up,
        tools=all_tools_for_model, # Keep tools available for potential further calls
        tool_choice="auto"
    )

    print("\n--- Final Model Response ---")
    print(follow_up_response.choices[0].message.content)

else:
    print("\n--- Model did not call any tools ---")
    print(f"Model's response: {message.content}")
```


## Direct Calling

You can also call MCP tools directly using `client.call()`:

```python
client.configure_tools(tools) # Configure the tools first

result = client.call("time_server-now", {})
print(result)
```

## Resources

Some MCP servers provide access to data sources called resources. The SDK automatically creates tools for listing and reading these resources:

- `{server_name}-list_resources`: Lists available resources.
- `{server_name}-read_resource`: Reads a resource by its URI.

```python
# List resources from the 'my_server'
resources = client.call("my_server-list_resources", {})

# Read a specific resource
content = client.call("my_server-read_resource", {"uri": "resource_uri"})
```

## Error Handling

The SDK is designed to handle MCP-related errors gracefully. If the `mcp` package is not installed, an `ImportError` will be raised. Connection errors and other issues are wrapped in the standard `HAIError` exceptions.