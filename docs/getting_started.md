# Quickstart

This guide provides a comprehensive walkthrough of the HelpingAI Python SDK, from installation to advanced usage. The SDK offers powerful features including built-in tools for code execution and web search, enhanced workflows that simplify development, and comprehensive tool calling capabilities.

## Key SDK Capabilities

- **Chat Completions**: Generate intelligent responses with the latest AI models
- **Built-in Tools**: Ready-to-use [`code_interpreter`](HelpingAI/tools/builtin_tools/code_interpreter.py:17) and [`web_search`](HelpingAI/tools/builtin_tools/web_search.py:17) tools
- **Enhanced Workflows**: Simplified tool calling with automatic caching and helper methods
- **Custom Tools**: Define your own tools using decorators or programmatic approaches
- **Streaming Support**: Real-time response streaming for better user experience
- **Comprehensive Error Handling**: Robust error management across all operations

## Installation

Install the HelpingAI SDK using pip:

```bash
pip install HelpingAI
```

## Setup

### 1. Get your API key

Your API key is available on your [HelpingAI Dashboard](https://helpingai.co/dashboard).

### 2. Set up your API key

We recommend using an environment variable to store your API key. This keeps your key secure and out of your codebase.

**For Unix/Linux/macOS:**
```bash
export HAI_API_KEY='your-api-key-here'
```

**For Windows Command Prompt:**
```cmd
set HAI_API_KEY=your-api-key-here
```

**For Windows PowerShell:**
```powershell
$env:HAI_API_KEY="your-api-key-here"
```

**Security Best Practices:**
- Never commit API keys to version control
- Use environment variables or secure configuration files
- Consider using a `.env` file with python-dotenv for local development
- Rotate your API keys regularly

### 3. Initialize the client

Create an instance of the [`HAI`](HelpingAI/client/main.py:20) client. If the `HAI_API_KEY` environment variable is set, the client will automatically use it. Otherwise, you can pass the key directly.

```python
from HelpingAI import HAI

# Initialize with environment variable (recommended)
client = HAI()

# Or, initialize with key directly (for testing only)
# client = HAI(api_key="your-api-key-here")

# With additional configuration
# client = HAI(
#     api_key="your-api-key-here",
#     timeout=30.0,  # Custom timeout
#     base_url="https://api.helpingai.co/v1"  # Custom endpoint
# )
```

## Make your first API call

You can now use the client to make API calls. Here's a practical example that demonstrates response handling and inspection:

```python
# Create a chat completion
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    temperature=0.7,
    max_tokens=150
)

# Access the response content
content = response.choices[0].message.content
print("Assistant:", content)

# Inspect response metadata
print(f"\nModel used: {response.model}")
print(f"Total tokens: {response.usage.total_tokens}")
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")

# Access response as dictionary (standard response structure)
response_dict = response.model_dump()
print(f"Response ID: {response_dict['id']}")
print(f"Created at: {response_dict['created']}")
```

**Example Output:**
```
Assistant: Quantum computing is like having a super-powered computer that can explore many possible solutions simultaneously...

Model used: Dhanishtha-2.0-preview
Total tokens: 145
Prompt tokens: 25
Completion tokens: 120
Response ID: chatcmpl-abc123
Created at: 1704067200
```

## Streaming

Streaming allows you to receive responses in real-time as they're generated, providing a better user experience for longer responses. This is particularly useful for chatbots, content generation, and interactive applications.

```python
# Basic streaming example
print("Assistant: ", end="", flush=True)

stream = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "system", "content": "You are a creative storyteller."},
        {"role": "user", "content": "Tell me a short story about a brave knight discovering a hidden treasure."}
    ],
    stream=True,
    temperature=0.8
)

# Process streaming chunks
for chunk in stream:
    if chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)

print("\n")  # New line after streaming completes
```

**Streaming with Error Handling:**

```python
import time

def stream_with_error_handling(messages, model="Dhanishtha-2.0-preview"):
    """Stream responses with comprehensive error handling."""
    try:
        print("Assistant: ", end="", flush=True)
        
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            timeout=30.0  # Set reasonable timeout
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
                
        print("\n")
        return full_response
        
    except Exception as e:
        print(f"\nError during streaming: {e}")
        return None

# Usage
messages = [
    {"role": "user", "content": "Explain the benefits of renewable energy."}
]
response = stream_with_error_handling(messages)
```

## Tool Calling

The HelpingAI SDK provides powerful tool calling capabilities that extend the AI models with external functions and services. The SDK includes built-in tools for common tasks and supports custom tool definitions.

### Built-in Tools Overview

The SDK comes with professionally developed built-in tools that are ready to use immediately:

- **[`code_interpreter`](HelpingAI/tools/builtin_tools/code_interpreter.py:17)**: Secure Python execution environment with data science libraries
- **[`web_search`](HelpingAI/tools/builtin_tools/web_search.py:17)**: Real-time web search using advanced search APIs

### Quick Start with Built-in Tools

```python
# Using built-in tools is as simple as passing their names
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{
        "role": "user",
        "content": "Calculate the fibonacci sequence up to 10 numbers and search for recent AI news"
    }],
    tools=["code_interpreter", "web_search"]  # Built-in tools
)

print(response.choices[0].message.content)
```

### Enhanced Workflow (Recommended)

The SDK provides an enhanced workflow with automatic tool caching that simplifies development:

```python
# Step 1: Use tools in chat completion (automatically cached)
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Analyze some data for me"}],
    tools=["code_interpreter", "web_search"]
)

# Step 2: Call tools directly using cached configuration
analysis_result = client.call("code_interpreter", {
    "code": """
import numpy as np
import matplotlib.pyplot as plt

# Generate sample data
data = np.random.normal(100, 15, 1000)
mean = np.mean(data)
std = np.std(data)

# Create visualization
plt.figure(figsize=(10, 6))
plt.hist(data, bins=30, alpha=0.7, edgecolor='black')
plt.axvline(mean, color='red', linestyle='--', label=f'Mean: {mean:.2f}')
plt.title('Sample Data Distribution')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.legend()
plt.show()

print(f"Analysis complete: Mean = {mean:.2f}, Std = {std:.2f}")
"""
})

print(f"Code execution result: {analysis_result}")
```

### Custom Tools with the @tools Decorator

Define your own tools using the [`@tools`](HelpingAI/tools/core.py:125) decorator:

```python
from HelpingAI.tools import tools

@tools
def get_weather(city: str, unit: str = "celsius") -> dict:
    """Get the current weather in a given city.

    Args:
        city (str): The city for which to get the weather.
        unit (str): The unit to use for the temperature. Can be either "celsius" or "fahrenheit".
    """
    # In a real implementation, this would call a weather API
    return {"city": city, "temperature": 22, "unit": unit}

# Use custom tools alongside built-in tools
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's the weather in Paris and search for weather forecasting methods?"}],
    tools=["web_search", get_weather],  # Mix built-in and custom tools
    tool_choice="auto"
)
```

### Traditional Tool Call Handling

For more control over tool execution, you can handle tool calls manually:

```python
import json

# Create initial response
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=[get_weather],
    tool_choice="auto"
)

message = response.choices[0].message

# Handle tool calls if present
if message.tool_calls:
    tool_messages = []
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Execute the tool
        result = client.call(function_name, function_args)
        
        tool_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result)
        })

    # Get final response with tool results
    follow_up_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "user", "content": "What's the weather in Paris?"},
            message,
            *tool_messages,
        ]
    )
    print(follow_up_response.choices[0].message.content)
```

## Working with Built-in Tools

The SDK's built-in tools provide powerful capabilities without any setup or configuration.

### Code Interpreter

The [`code_interpreter`](HelpingAI/tools/builtin_tools/code_interpreter.py:17) tool provides a secure Python execution environment with data science libraries:

```python
# Mathematical calculations
math_result = client.call("code_interpreter", {
    "code": """
import math

# Calculate compound interest
principal = 1000
rate = 0.05
time = 10

amount = principal * (1 + rate) ** time
interest = amount - principal

print(f"Principal: ${principal}")
print(f"Rate: {rate*100}%")
print(f"Time: {time} years")
print(f"Final Amount: ${amount:.2f}")
print(f"Interest Earned: ${interest:.2f}")
"""
})

# Data visualization
viz_result = client.call("code_interpreter", {
    "code": """
import numpy as np
import matplotlib.pyplot as plt

# Create a simple data visualization
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y1, label='sin(x)', color='blue')
plt.plot(x, y2, label='cos(x)', color='red')
plt.title('Trigonometric Functions')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.show()

print("Visualization created successfully!")
"""
})
```

### Web Search

The [`web_search`](HelpingAI/tools/builtin_tools/web_search.py:17) tool provides real-time web search capabilities:

```python
# Current events search
news_results = client.call("web_search", {
    "query": "latest developments in artificial intelligence 2024",
    "max_results": 5
})

# Technical information search
tech_results = client.call("web_search", {
    "query": "Python best practices for machine learning",
    "max_results": 3
})

print(f"Found {len(news_results.get('results', []))} news articles")
print(f"Found {len(tech_results.get('results', []))} technical resources")
```

## Enhanced Workflows

The SDK provides enhanced workflows that reduce boilerplate code and simplify development.

### Automatic Tool Caching

Tools used in [`chat.completions.create()`](HelpingAI/client/completions.py:110) are automatically cached and available for direct calling:

```python
# Tools are automatically cached after first use
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Help me with data analysis"}],
    tools=["code_interpreter", "web_search", get_weather]
)

# Now you can call any of these tools directly without reconfiguration
code_result = client.call("code_interpreter", {"code": "print('Hello World')"})
search_result = client.call("web_search", {"query": "data analysis tools"})
weather_result = client.call("get_weather", {"city": "London"})
```

### Helper Methods for Complex Workflows

Use helper methods to simplify tool call handling:

```python
# Using helper methods for streamlined workflows
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Analyze sales data and create a report"}],
    tools=["code_interpreter", "web_search"]
)

# If the model made tool calls, execute them automatically
if response.choices[0].message.tool_calls:
    # Execute all tool calls
    execution_results = client.chat.completions.execute_tool_calls(
        response.choices[0].message
    )
    
    # Create tool response messages
    tool_messages = client.chat.completions.create_tool_response_messages(
        execution_results
    )
    
    # Get final response
    final_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "user", "content": "Analyze sales data and create a report"},
            response.choices[0].message,
            *tool_messages
        ]
    )
    print(final_response.choices[0].message.content)
```

## Error Handling

Implement proper error handling for robust applications:

```python
from HelpingAI.tools.errors import ToolExecutionError
import json

def safe_tool_calling():
    """Example of safe tool calling with error handling."""
    try:
        # Attempt to use tools
        response = client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[{"role": "user", "content": "Calculate something complex"}],
            tools=["code_interpreter"],
            timeout=30.0
        )
        
        # Safe tool execution
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                try:
                    result = client.call(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments)
                    )
                    print(f"Tool {tool_call.function.name} executed successfully")
                except ToolExecutionError as e:
                    print(f"Tool execution failed: {e}")
                except json.JSONDecodeError as e:
                    print(f"Invalid tool arguments: {e}")
                    
    except Exception as e:
        print(f"Request failed: {e}")

# Run safe tool calling
safe_tool_calling()
```

## Best Practices

Follow these best practices for effective SDK usage:

### 1. Use Built-in Tools When Possible
```python
# Prefer built-in tools for common tasks
tools = ["code_interpreter", "web_search"]  # Ready-to-use, well-tested
```

### 2. Leverage Enhanced Workflows
```python
# Use automatic caching to reduce configuration overhead
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Help with analysis"}],
    tools=["code_interpreter"]  # Automatically cached
)

# Direct calling without reconfiguration
result = client.call("code_interpreter", {"code": "print('Cached tool!')"})
```

### 3. Implement Error Handling
```python
# Always wrap tool calls in try-except blocks
try:
    result = client.call("code_interpreter", {"code": "complex_calculation()"})
except ToolExecutionError as e:
    print(f"Execution failed: {e}")
```

### 4. Use Appropriate Timeouts
```python
# Set reasonable timeouts for long-running operations
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=["code_interpreter"],
    timeout=60.0  # Adequate for complex computations
)
```

### 5. Optimize Tool Selection
```python
# Only include tools that are relevant to the task
tools = ["web_search"]  # For information retrieval
# tools = ["code_interpreter"]  # For calculations/analysis
# tools = ["web_search", "code_interpreter"]  # For comprehensive tasks
```

## Next steps

Now that you have the basics down, you can explore the full capabilities of the SDK:

### Essential Documentation

- **[API Reference](api_reference.md)**: Comprehensive documentation of all classes, methods, and built-in tools
- **[Tool Calling Guide](tool_calling.md)**: In-depth guide to custom tools, advanced workflows, and MCP integration
- **[Examples](examples.md)**: Practical examples covering built-in tools, enhanced workflows, and real-world use cases

### Recommended Learning Path

1. **Start with Built-in Tools**: Experiment with [`code_interpreter`](HelpingAI/tools/builtin_tools/code_interpreter.py:17) and [`web_search`](HelpingAI/tools/builtin_tools/web_search.py:17) for immediate productivity
2. **Adopt Enhanced Workflows**: Use automatic tool caching and helper methods to reduce development time
3. **Create Custom Tools**: Define your own tools using the [`@tools`](HelpingAI/tools/core.py:125) decorator for specific needs
4. **Explore Advanced Features**: Learn about streaming, error handling, and performance optimization

### Choosing Your Approach

- **For Quick Prototyping**: Use built-in tools with enhanced workflows
- **For Production Applications**: Implement comprehensive error handling and custom tools
- **For Complex Integrations**: Explore MCP servers and advanced tool configurations
- **For Performance-Critical Apps**: Study the API reference for optimization techniques

### Community and Support

- Review the [examples](examples.md) for inspiration and common patterns
- Check the [FAQ](faq.md) for solutions to common issues
- Explore the [tool calling guide](tool_calling.md) for advanced techniques