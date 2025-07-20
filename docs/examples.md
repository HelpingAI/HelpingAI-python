# Examples

This page provides a variety of examples to help you get started with the HelpingAI Python SDK.

## Basic Chat Completion

This example demonstrates how to make a basic, non-streaming chat completion request to the HelpingAI API. This is suitable for single-turn interactions where you want the complete response at once.

```python
from HelpingAI import HAI

# Initialize the client. It will automatically pick up the API key from the HAI_API_KEY environment variable.
# Alternatively, you can pass it directly: client = HAI(api_key="your_api_key")
client = HAI()

# Define the messages for the conversation.
# The 'messages' parameter expects a list of dictionaries, each with a 'role' and 'content'.
# Common roles include "user", "assistant", and "system".
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "What is the capital of Canada?"}
]

# Create the chat completion.
# The 'model' parameter specifies which AI model to use.
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview", # Or another available model like "Helpingai3-raw"
    messages=messages
)

# Access the content of the model's response.
# The response object contains a list of 'choices', and each choice has a 'message' object.
print("Model's response:")
print(response.choices[0].message.content)

# You can also inspect other parts of the response, like token usage:
if response.usage:
    print(f"\nToken Usage: ")
    print(f"  Prompt Tokens: {response.usage.prompt_tokens}")
    print(f"  Completion Tokens: {response.usage.completion_tokens}")
    print(f"  Total Tokens: {response.usage.total_tokens}")
```

## Streaming Completions

Streaming allows you to receive and process the model's response incrementally, token by token, as it is generated. This is particularly useful for real-time applications like chatbots, as it provides a more responsive user experience.

To enable streaming, set the `stream` parameter to `True` in the `client.chat.completions.create()` method. The method will then return an iterator that yields `ChatCompletionChunk` objects.

```python
from HelpingAI import HAI

client = HAI()

# Define the messages for the conversation.
messages = [
    {"role": "user", "content": "Tell me a detailed story about a brave knight who embarks on a quest to find a legendary dragon."}
]

print("\nStreaming response:")
# Create a streaming chat completion.
stream = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    stream=True # Enable streaming
)

# Iterate over the chunks received from the stream.
# Each chunk contains a 'delta' object with the newly generated content.
for chunk in stream:
    # Check if there's new content in the current chunk
    if chunk.choices[0].delta.content:
        # Print the content without a newline to show continuous generation
        print(chunk.choices[0].delta.content, end="")
    # You can also check for finish_reason to know when the stream ends
    if chunk.choices[0].finish_reason:
        print(f"\n\nFinish Reason: {chunk.choices[0].finish_reason}")

print("\nStreaming complete.")
```

## Tool Calling

The HelpingAI SDK's tool calling capability allows models to interact with external functions and services. This section provides examples demonstrating how to define tools, enable the model to use them, and handle tool calls.

### Defining a Tool

Tools can be defined using the `@tools` decorator, which automatically generates a JSON schema from your Python function's signature and docstring.

```python
from HelpingAI.tools import tools
from typing import Literal

@tools
def get_current_weather(location: str, unit: Literal["celsius", "fahrenheit"] = "celsius") -> dict:
    """Get the current weather in a given location.

    Args:
        location (str): The city and state, e.g., "San Francisco, CA".
        unit (Literal["celsius", "fahrenheit"], optional): The unit of temperature to use.
            Defaults to "celsius".
    """
    # In a real application, this would call an external weather API
    if location.lower() == "paris":
        temperature = 22 if unit == "celsius" else 71.6
    elif location.lower() == "london":
        temperature = 15 if unit == "celsius" else 59.0
    else:
        temperature = "N/A"

    print(f"[Tool Call] get_current_weather(location='{location}', unit='{unit}')")
    return {"location": location, "temperature": temperature, "unit": unit}

@tools
def get_stock_price(symbol: str) -> dict:
    """Retrieves the current stock price for a given stock symbol.

    Args:
        symbol (str): The stock ticker symbol (e.g., GOOG, AAPL).
    """
    print(f"[Tool Call] get_stock_price(symbol='{symbol}')")
    prices = {"GOOG": 170.00, "AAPL": 180.50, "MSFT": 420.00}
    return {"symbol": symbol, "price": prices.get(symbol.upper(), "N/A")}
```

### Using Tools in Chat Completions

To enable the model to use your defined tools, pass them to the `tools` parameter of `client.chat.completions.create()`. The `tool_choice` parameter controls how the model uses tools.

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools
import json

client = HAI()

# Get all tools registered with the @tools decorator
available_tools = get_tools()

# Example 1: Model decides to call a single tool
print("--- Example 1: Single Tool Call ---")
messages_1 = [{"role": "user", "content": "What's the weather in Paris?"}]
response_1 = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages_1,
    tools=available_tools,
    tool_choice="auto"
)

message_1 = response_1.choices[0].message

if message_1.tool_calls:
    print("\nModel wants to call tools:")
    tool_messages_1 = []
    for tool_call in message_1.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print(f"- Calling tool: {function_name} with args: {function_args}")
        result = client.call(function_name, function_args) # Execute the tool
        print(f"  Tool result: {result}")

        tool_messages_1.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result)
        })

    # Continue the conversation with the tool results
    follow_up_response_1 = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages_1 + [message_1] + tool_messages_1,
        tools=available_tools, # Keep tools available for potential further calls
        tool_choice="auto"
    )
    print("\nFinal model response after tool execution:")
    print(follow_up_response_1.choices[0].message.content)
else:
    print("\nModel did not call any tools.")
    print(f"Model's response: {message_1.content}")

# Example 2: Model decides to call multiple tools
print("\n--- Example 2: Multiple Tool Calls ---")
messages_2 = [{"role": "user", "content": "What's the weather in London and the stock price of GOOG?"}]
response_2 = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages_2,
    tools=available_tools,
    tool_choice="auto"
)

message_2 = response_2.choices[0].message

if message_2.tool_calls:
    print("\nModel wants to call multiple tools:")
    tool_messages_2 = []
    for tool_call in message_2.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print(f"- Calling tool: {function_name} with args: {function_args}")
        result = client.call(function_name, function_args) # Execute the tool
        print(f"  Tool result: {result}")

        tool_messages_2.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result)
        })

    # Continue the conversation with the tool results
    follow_up_response_2 = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages_2 + [message_2] + tool_messages_2,
        tools=available_tools,
        tool_choice="auto"
    )
    print("\nFinal model response after multiple tool executions:")
    print(follow_up_response_2.choices[0].message.content)
else:
    print("\nModel did not call any tools.")
    print(f"Model's response: {message_2.content}")

# Example 3: Forcing a tool call
print("\n--- Example 3: Forcing a Tool Call ---")
messages_3 = [{"role": "user", "content": "Just tell me the weather in London."}]
response_3 = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages_3,
    tools=available_tools,
    tool_choice={"type": "function", "function": {"name": "get_current_weather"}} # Force the model to call this tool
)

message_3 = response_3.choices[0].message

if message_3.tool_calls:
    print("\nModel was forced to call a tool:")
    tool_messages_3 = []
    for tool_call in message_3.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print(f"- Calling tool: {function_name} with args: {function_args}")
        result = client.call(function_name, function_args)
        print(f"  Tool result: {result}")

        tool_messages_3.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result)
        })

    follow_up_response_3 = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages_3 + [message_3] + tool_messages_3,
        tools=available_tools,
        tool_choice="auto"
    )
    print("\nFinal model response after forced tool execution:")
    print(follow_up_response_3.choices[0].message.content)
else:
    print("\nModel did not call any tools (unexpected for forced call).")
    print(f"Model's response: {message_3.content}")

# Example 4: Using hide_think parameter
print("\n--- Example 4: Using hide_think parameter ---")
messages_4 = [{"role": "user", "content": "Tell me a story about a brave knight."}]
response_4_stream = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages_4,
    stream=True,
    hide_think=True # Filter out internal reasoning
)

print("\nStreaming response with hide_think=True:")
for chunk in response_4_stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
print() # Newline after streaming

response_4_non_stream = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages_4,
    hide_think=True # Filter out internal reasoning
)
print("\nNon-streaming response with hide_think=True:")
print(response_4_non_stream.choices[0].message.content)

```

## Error Handling

This example shows how to handle API errors.

```python
from HelpingAI import HAI, HAIError

client = HAI()

try:
    response = client.chat.completions.create(
        model="invalid-model",
        messages=[
            {"role": "user", "content": "Hello, world!"}
        ]
    )
except HAIError as e:
    print(f"An API error occurred: {e}")
```