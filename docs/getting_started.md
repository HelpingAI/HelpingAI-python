# Quickstart

This guide provides a comprehensive walkthrough of the HelpingAI Python SDK, from installation to advanced usage.

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

```bash
export HAI_API_KEY='your-api-key-here'
```

### 3. Initialize the client

Create an instance of the `HAI` client. If the `HAI_API_KEY` environment variable is set, the client will automatically use it. Otherwise, you can pass the key directly.

```python
from HelpingAI import HAI

# Initialize with environment variable
client = HAI()

# Or, initialize with key directly
# client = HAI(api_key="your-api-key-here")
```

## Make your first API call

You can now use the client to make API calls. For example, you can create a chat completion:

```python
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Hello, world!"}
    ]
)

print(response.choices[0].message.content)
```

## Streaming

To stream responses, set the `stream` parameter to `True`.

```python
stream = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Tell me a story about a brave knight."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Tool Calling

The HelpingAI SDK supports tool calling, allowing you to extend the capabilities of the models.

### 1. Define a tool

Use the `@tools` decorator to define a tool.

```python
from HelpingAI.tools import tools

@tools
def get_weather(city: str, unit: str = "celsius") -> dict:
    """Get the current weather in a given city.

    Args:
        city (str): The city for which to get the weather.
        unit (str): The unit to use for the temperature. Can be either "celsius" or "fahrenheit".
    """
    return {"city": city, "temperature": 22, "unit": unit}
```

### 2. Use the tool

Pass the tool to the `tools` parameter of the `client.chat.completions.create()` method.

```python
from HelpingAI.tools import get_tools

response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=get_tools(),
    tool_choice="auto"
)
```

### 3. Handle the tool call

If the model decides to use the tool, you can execute it using `client.call()`.

```python
import json

message = response.choices[0].message

if message.tool_calls:
    tool_messages = []
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        result = client.call(function_name, function_args)
        
        tool_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result)
        })

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

## Next steps

Now that you have the basics down, you can explore the full capabilities of the SDK:

- **[API Reference](api_reference.md)**: For detailed information on all classes and methods.
- **[Tool Calling Guide](tool_calling.md)**: To learn how to use tools with the SDK.
- **[Examples](examples.md)**: For more complex examples and use cases.