# API Reference

This document provides a detailed reference for the HelpingAI Python SDK. For a quick start, see our [Getting Started Guide](getting_started.md).

## Client Initialization

The `HAI` class is the primary entry point for interacting with the HelpingAI API. It provides a convenient and robust interface for accessing various API functionalities, including chat completions, model information, and tool execution.

You must initialize the client with your API key, which can be obtained from your [HelpingAI Dashboard](https://helpingai.co/dashboard).

### `HAI(...)`

```python
class HAI:
    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0
    )
```

**Parameters:**

- `api_key` (str, optional): Your HelpingAI API key. This is crucial for authenticating your requests. If not provided directly during initialization, the SDK will automatically attempt to retrieve it from the `HAI_API_KEY` environment variable.
  
  *Example:*
  ```python
  client = HAI(api_key="your_secret_api_key")
  ```
  Or, by setting an environment variable:
  ```bash
  export HAI_API_KEY="your_secret_api_key"
  ```
  ```python
  client = HAI() # Automatically picks up HAI_API_KEY
  ```

- `organization` (str, optional): An optional identifier for your organization. If you belong to multiple organizations within HelpingAI, specifying this parameter ensures your requests are attributed correctly.

- `base_url` (str, optional): The base URL for the HelpingAI API. This parameter is useful for directing requests to a custom endpoint, such as a proxy or a different API version. By default, it points to the official HelpingAI API endpoint: `https://api.helpingai.co/v1`.

- `timeout` (float, optional): The maximum duration (in seconds) to wait for an API response. This helps prevent requests from hanging indefinitely. The default timeout is `60.0` seconds.

**Attributes:**

Once initialized, the `HAI` client provides access to the following key API interfaces:

- `client.chat`: Provides methods for interacting with the Chat Completions API, primarily `client.chat.completions.create()`.
- `client.models`: Offers methods for listing and retrieving information about available models, such as `client.models.list()` and `client.models.retrieve()`.


## Chat Completions

The Chat Completions API allows you to generate text-based completions for a given prompt.

### `client.chat.completions.create(...)`

```python
def create(
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    stop: Optional[Union[str, List[str]]] = None,
    stream: bool = False,
    user: Optional[str] = None,
    n: Optional[int] = None,
    logprobs: Optional[bool] = None,
    top_logprobs: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None,
    seed: Optional[int] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = "auto",
    hide_think: bool = False
) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]
```

**Parameters:**

- `model` (str, required): The ID of the model to use for the completion. This specifies which AI model will process your request (e.g., `"Dhanishtha-2.0-preview"`).
- `messages` (List[Union[Dict[str, Any], BaseModel]], required): A list of message objects representing the conversation history. Each message must have a `role` (e.g., `"user"`, `"assistant"`, `"system"`, `"tool"`) and `content`. You can also pass `BaseModel` objects like `ChatCompletionMessage` directly.
  
  *Example:*
  ```python
  messages = [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of France?"}
  ]
  ```
- `temperature` (float, optional): Controls the randomness of the output. A higher value (e.g., `0.8`) makes the output more random, while a lower value (e.g., `0.2`) makes it more deterministic. Values typically range from `0.0` to `1.0`. Defaults to `None` (model's default temperature).
- `max_tokens` (int, optional): The maximum number of tokens (words or sub-words) to generate in the completion. The API will stop generating tokens once this limit is reached. Defaults to `None` (model's maximum context length).
- `top_p` (float, optional): An alternative to sampling with `temperature`, called nucleus sampling. The model considers the tokens whose cumulative probability mass exceeds `top_p`. For example, `0.1` means the model considers only the tokens comprising the top 10% probability mass. Defaults to `None`.
- `frequency_penalty` (float, optional): Penalizes new tokens based on their existing frequency in the text so far. This reduces the likelihood of the model repeating the same phrases. Values typically range from `-2.0` to `2.0`. Defaults to `0.0`.
- `presence_penalty` (float, optional): Penalizes new tokens based on whether they appear in the text so far. This encourages the model to talk about new topics. Values typically range from `-2.0` to `2.0`. Defaults to `0.0`.
- `stop` (Union[str, List[str]], optional): A sequence or list of sequences where the API will stop generating further tokens. The generated text will not contain the stop sequence. You can specify up to 4 stop sequences. Defaults to `None`.
- `stream` (bool, optional): If `True`, the response will be streamed back as a series of `ChatCompletionChunk` objects, allowing you to process tokens as they are generated. If `False`, the API will return a single `ChatCompletion` object once the entire completion is ready. Defaults to `False`.
- `user` (str, optional): A unique identifier representing your end-user. This can help HelpingAI to monitor and detect abuse, and is recommended for best practices. Defaults to `None`.
- `n` (int, optional): The number of chat completion choices to generate for each input message. Note that generating multiple completions will consume more tokens. Defaults to `1`.
- `logprobs` (bool, optional): If `True`, the response will include the log probabilities of the output tokens, which can be useful for analyzing model confidence. Defaults to `False`.
- `top_logprobs` (int, optional): An integer between `0` and `20` specifying the number of top log probabilities to return. This parameter is only effective when `logprobs` is `True`. Defaults to `0`.
- `response_format` (Dict[str, str], optional): An object specifying the format that the model must output. Currently, the only supported format is `{"type": "json_object"}` for JSON mode. When using JSON mode, you must instruct the model to produce JSON in the system or user message. Defaults to `None`.
- `seed` (int, optional): This feature is in Beta. If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same `seed` and parameters should return the same result. This is useful for reproducibility. Defaults to `None`.
- `tools` (Optional[Union[List[Dict[str, Any]], List[Fn], str]]): A list of tools the model may call. This parameter supports various formats for flexibility:
    - `List[Dict[str, Any]]`: A list of tool definitions in the standard tool definition format (e.g., `{"type": "function", "function": {"name": "my_tool", ...}}`).
    - `List[Fn]`: A list of `Fn` objects, which are programmatic representations of tools created using the `@tools` decorator or `Fn` class.
    - `str`: A category name (e.g., `"built_in"`) to automatically include a predefined set of tools from the SDK's registry.
  Defaults to `None`.
- `tool_choice` (Union[str, Dict[str, Any]], optional): Controls which (if any) function is called by the model.
    - `"auto"` (default): The model can decide whether to call a tool or generate a message.
    - `"none"`: The model will not call a tool and will generate a message.
    - `{"type": "function", "function": {"name": "my_tool"}}`: Forces the model to call a specific tool.
  Defaults to `"auto"`.
- `hide_think` (bool, optional): If `True`, filters out the model's internal reasoning blocks (e.g., `<think>...</think>` and `<ser>...</ser>`) from the output content. This is useful for cleaner, production-ready output. Defaults to `False`.

**Returns:**

- If `stream=False`, a `ChatCompletion` object, which is a dataclass representing the complete chat completion response.
- If `stream=True`, an `Iterator[ChatCompletionChunk]`, which yields `ChatCompletionChunk` dataclass objects as the response streams.

## Models

The Models API allows you to list and retrieve information about the AI models available through the HelpingAI platform.

### `client.models.list()`

```python
def list() -> List[Model]
```

Retrieves a comprehensive list of all AI models currently available in the HelpingAI ecosystem. This includes details such as their IDs, names, and descriptions.

**Returns:**

- `List[Model]`: A list of `Model` objects, each containing metadata about an available AI model.

**Raises:**

- `APIError`: If there is an issue communicating with the HelpingAI API.
- `AuthenticationError`: If the provided API key is invalid or missing.

### `client.models.retrieve(...)`

```python
def retrieve(model_id: str) -> Model
```

Retrieves detailed information about a specific AI model by its unique identifier.

**Parameters:**

- `model_id` (str, required): The unique ID of the model to retrieve (e.g., `"Dhanishtha-2.0-preview"`).

**Returns:**

- `Model`: A `Model` object containing detailed information about the requested model.

**Raises:**

- `ValueError`: If the specified `model_id` does not correspond to an existing model.
- `APIError`: If there is an issue communicating with the HelpingAI API.
- `AuthenticationError`: If the provided API key is invalid or missing.

## Built-in Tools

The HelpingAI SDK includes powerful built-in tools that provide essential functionality for AI applications. These tools are automatically available and can be used in chat completions or called directly.

### `code_interpreter`

The [`code_interpreter`](HelpingAI/tools/builtin_tools/code_interpreter.py:26) tool provides Python code execution in a secure sandboxed environment with comprehensive data science capabilities.

**Features:**

- **Secure Sandbox**: Executes Python code in an isolated environment with timeout protection (default: 30 seconds)
- **Data Science Libraries**: Automatic imports for popular libraries including [`numpy`](HelpingAI/tools/builtin_tools/code_interpreter.py:169), [`pandas`](HelpingAI/tools/builtin_tools/code_interpreter.py:174), [`matplotlib`](HelpingAI/tools/builtin_tools/code_interpreter.py:179), and [`seaborn`](HelpingAI/tools/builtin_tools/code_interpreter.py:188)
- **Plot Generation**: Automatic plot saving with [`matplotlib`](HelpingAI/tools/builtin_tools/code_interpreter.py:179) integration and non-interactive backend
- **File Handling**: Working directory management for file operations and data persistence
- **Error Handling**: Comprehensive error reporting with timeout protection

**Parameters:**

- `code` (str, required): Python code to execute in the sandbox environment

**Configuration Options:**

- `timeout` (int, optional): Execution timeout in seconds (default: 30)
- `work_dir` (str, optional): Working directory for code execution

**Usage Examples:**

```python
# Using in chat completions
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Calculate the mean of [1, 2, 3, 4, 5] using numpy"}],
    tools=["code_interpreter"]
)

# Direct tool calling
result = client.call("code_interpreter", {
    "code": """
import numpy as np
data = [1, 2, 3, 4, 5]
mean_value = np.mean(data)
print(f"Mean: {mean_value}")
"""
})
```

### `web_search`

The [`web_search`](HelpingAI/tools/builtin_tools/web_search.py:17) tool provides real-time web search functionality using the Snapzion Search API.

**Features:**

- **Real-time Search**: Access to current web information with high-quality results
- **Comprehensive Results**: Returns titles, snippets, URLs, source information, and search positions
- **Configurable Limits**: Adjustable result count (1-10 results)
- **Structured Output**: Well-formatted results with metadata for easy processing

**Parameters:**

- `query` (str, required): Search query to look up on the web
- `max_results` (int, optional): Maximum number of search results to return (default: 5, max: 10)

**Usage Examples:**

```python
# Using in chat completions
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's the latest news about AI developments?"}],
    tools=["web_search"]
)

# Direct tool calling
search_results = client.call("web_search", {
    "query": "latest AI developments 2024",
    "max_results": 3
})
```

**Result Format:**

The web search tool returns formatted results including:
- **Title**: Page title from search results
- **Snippet**: Brief description or excerpt from the page
- **URL**: Direct link to the source page
- **Source**: Domain or source identifier
- **Position**: Search result ranking position

## Tool Calling

The HelpingAI SDK provides a powerful and flexible framework for defining and using tools with the Chat Completions API. This allows the AI models to interact with external functions, services, and data sources.

### `client.call(...)`

```python
def call(self, tool_name: str, arguments: Union[Dict[str, Any], str, set], tools: Optional[Union[List[Dict[str, Any]], List, str]] = None) -> Any:
```

Directly calls a registered tool by its name, executing its associated function with the provided arguments. This method supports an enhanced workflow where tools from recent [`chat.completions.create()`](HelpingAI/client/completions.py:110) calls are automatically cached and available for direct calling.

**Enhanced Tool Workflow:**

The [`client.call()`](HelpingAI/client/main.py:107) method features automatic tool configuration caching that enables seamless workflows:

1. **Automatic Caching**: Tools used in [`chat.completions.create()`](HelpingAI/client/completions.py:110) are automatically cached
2. **Direct Calling**: After a chat completion with tools, you can immediately call those tools without reconfiguration
3. **Fallback Priority**: Uses explicitly configured tools first, then falls back to cached tools from recent chat calls

**Parameters:**

- `tool_name` (str, required): The unique name of the tool to be called (e.g., `"get_weather"`, `"code_interpreter"`, `"web_search"`).
- `arguments` (Union[Dict[str, Any], str, set], required): The arguments to pass to the tool's function. This can be a dictionary, a JSON string, or in some cases, a set (though a warning will be issued for sets, recommending dictionary or JSON string).
- `tools` (Optional[Union[List[Dict[str, Any]], List, str]], optional): An optional parameter to configure tools specifically for this `call` invocation. If provided, these tools will be registered and available for this call. This is useful for one-off tool configurations without affecting the client's global tool settings.

**Enhanced Workflow Examples:**

```python
# Method 1: Explicit configuration then calling
client.configure_tools(["code_interpreter", "web_search"])
result = client.call("code_interpreter", {"code": "print('Hello World')"})

# Method 2: Automatic caching workflow (recommended)
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Search for Python tutorials"}],
    tools=["web_search", "code_interpreter"]
)

# Tools are now automatically cached - can call directly
search_result = client.call("web_search", {
    "query": "Python programming tutorials 2024",
    "max_results": 5
})
```

**Returns:**

- `Any`: The result returned by the executed tool's function.

**Raises:**

- `ValueError`: If the specified `tool_name` is not found, or if the `arguments` are invalid or cannot be processed. Provides helpful guidance on tool configuration.
- `ToolExecutionError`: If an error occurs during the execution of the tool's function.

### `client.configure_tools(...)`

```python
def configure_tools(self, tools: Optional[Union[List[Dict[str, Any]], List, str]]) -> None:
```

Configures the set of tools available for the `HAI` client instance. Tools configured here will be accessible for subsequent `client.call()` invocations and can be used by the chat completions API if passed in the `create` method.

**Parameters:**

- `tools` (Optional[Union[List[Dict[str, Any]], List, str]], required): The tools configuration. This can be:
    - `List[Dict[str, Any]]`: A list of tool definitions in the standard tool definition format, including MCP server configurations.
    - `List[str]`: A list of built-in tool names (e.g., `"code_interpreter"`, `"web_search"`).
    - `None`: Clears any previously configured tools.

**Example:**

```python
client.configure_tools([
    # Example MCP server configuration
    {
        'mcpServers': {
            'time': {'command': 'uvx', 'args': ['mcp-server-time']},
            'fetch': {'command': 'uvx', 'args': ['mcp-server-fetch']}
        }
    },
    'code_interpreter', # Built-in tool
    'web_search'      # Built-in tool
])
```

## Chat Completions Helper Methods

The Chat Completions API includes several helper methods that simplify working with tool calls and message creation.

### `client.chat.completions.create_assistant_message(...)`

```python
def create_assistant_message(
    self,
    content: Optional[str] = None,
    tool_calls: Optional[List[Union[ToolCall, Dict[str, Any]]]] = None,
    function_call: Optional[Union[FunctionCall, Dict[str, Any]]] = None
) -> ChatCompletionMessage:
```

Creates an assistant message with automatic tool call conversion, making it easy to create properly formatted messages for conversation history.

**Parameters:**

- `content` (Optional[str]): The message content
- `tool_calls` (Optional[List[Union[ToolCall, Dict[str, Any]]]]): List of tool calls (ToolCall objects or dicts)
- `function_call` (Optional[Union[FunctionCall, Dict[str, Any]]]): Function call (FunctionCall object or dict)

**Returns:**

- `ChatCompletionMessage`: Properly formatted message object compatible with the standard tool definition format

### `client.chat.completions.execute_tool_calls(...)`

```python
def execute_tool_calls(
    self,
    message: ChatCompletionMessage,
    registry=None
) -> List[Dict[str, Any]]:
```

Executes all tool calls in a message and returns structured results, enabling automated tool execution workflows.

**Parameters:**

- `message` (ChatCompletionMessage, required): Message containing tool calls to execute
- `registry` (optional): Tool registry to use (uses global registry if None)

**Returns:**

- `List[Dict[str, Any]]`: List of execution results with format:
  ```python
  [{"tool_call_id": str, "result": Any, "error": str}]
  ```

### `client.chat.completions.create_tool_response_messages(...)`

```python
def create_tool_response_messages(
    self,
    execution_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
```

Creates tool response messages from execution results, automatically formatting them for conversation history.

**Parameters:**

- `execution_results` (List[Dict[str, Any]], required): Results from [`execute_tool_calls()`](HelpingAI/client/completions.py:305)

**Returns:**

- `List[Dict[str, Any]]`: List of properly formatted tool response messages

**Complete Tool Execution Workflow Example:**

```python
# 1. Create chat completion with tools
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Search for Python tutorials and analyze the results"}],
    tools=["web_search", "code_interpreter"]
)

# 2. Check if the model made tool calls
assistant_message = response.choices[0].message
if assistant_message.tool_calls:
    # 3. Execute the tool calls
    execution_results = client.chat.completions.execute_tool_calls(assistant_message)
    
    # 4. Create tool response messages
    tool_responses = client.chat.completions.create_tool_response_messages(execution_results)
    
    # 5. Continue the conversation with tool results
    messages = [
        {"role": "user", "content": "Search for Python tutorials and analyze the results"},
        assistant_message.to_dict(),  # Convert to dict for API
        *tool_responses  # Add tool responses
    ]
    
    # 6. Get final response with tool results
    final_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages
    )
```

## Response Objects

This section provides detailed descriptions of the data structures returned by the HelpingAI API. All response objects inherit from [`BaseModel`](HelpingAI/base_models.py:27), which provides enhanced functionality including dictionary-like access patterns and Pydantic compatibility.

### BaseModel Enhancements

All response objects in the HelpingAI SDK inherit from [`BaseModel`](HelpingAI/base_models.py:27), providing powerful features for data access and manipulation:

**Dictionary-like Access Patterns:**

```python
# All response objects support dictionary-style access
response = client.chat.completions.create(...)
message = response.choices[0].message

# Dictionary-style access
content = message["content"]
role = message["role"]

# Check if key exists
if "tool_calls" in message:
    tool_calls = message["tool_calls"]

# Get with default value
content = message.get("content", "No content")

# Iterate like a dictionary
for key, value in message.items():
    print(f"{key}: {value}")

# Get all keys, values
keys = list(message.keys())
values = list(message.values())
```

**Pydantic Compatibility Methods:**

```python
# Convert to dictionary (Pydantic-style)
message_dict = message.model_dump()

# Convert to JSON string (Pydantic-style)
message_json = message.model_dump_json()

# Create from dictionary (Pydantic-style)
new_message = ChatCompletionMessage.model_validate({
    "role": "assistant",
    "content": "Hello!"
})

# Standard methods also available
message_dict = message.to_dict()
message_json = message.json()
```

**Enhanced JSON Serialization:**

```python
import json
from HelpingAI.base_models import json_dumps

# Automatic BaseModel handling in JSON serialization
data = {
    "message": message,
    "choices": response.choices
}

# This automatically converts BaseModel objects
json_string = json_dumps(data)

# Or use the built-in json() method
json_string = response.json()
```

### `ChatCompletion`

Represents a complete chat completion response from the API when `stream=False`.

**Attributes:**

- `id` (str): A unique identifier for the chat completion.
- `created` (int): The Unix timestamp (in seconds) when the chat completion was created.
- `model` (str): The ID of the model used for the completion.
- `choices` (List[Choice]): A list of `Choice` objects, each representing a possible completion generated by the model.
- `object` (str): The type of object, always `"chat.completion"`.
- `system_fingerprint` (Optional[str]): A fingerprint representing the system configuration that generated the response. Can be used for debugging.
- `usage` (Optional[CompletionUsage]): An object containing information about the token usage for the completion.

### `ChatCompletionChunk`

Represents a single chunk of a streaming chat completion response from the API when `stream=True`.

**Attributes:**

- `id` (str): A unique identifier for the chat completion chunk.
- `created` (int): The Unix timestamp (in seconds) when the chunk was created.
- `model` (str): The ID of the model used for the completion.
- `choices` (List[Choice]): A list of `Choice` objects, each containing a `delta` that represents a partial completion.
- `object` (str): The type of object, always `"chat.completion.chunk"`.
- `system_fingerprint` (Optional[str]): A fingerprint representing the system configuration that generated the response. Can be used for debugging.

### `Choice`

Represents a single completion choice within a `ChatCompletion` or `ChatCompletionChunk`.

**Attributes:**

- `index` (int): The index of the choice in the list of choices.
- `message` (Optional[ChatCompletionMessage]): A `ChatCompletionMessage` object containing the full message content for non-streaming responses.
- `delta` (Optional[ChoiceDelta]): A `ChoiceDelta` object containing the partial message content for streaming responses.
- `finish_reason` (Optional[str]): The reason the model stopped generating tokens (e.g., `"stop"`, `"length"`, `"tool_calls"`, `"content_filter"`).
- `logprobs` (Optional[Dict[str, Any]]): Log probability information for the generated tokens, if `logprobs` was enabled in the request.

### `ChatCompletionMessage`

Represents a message in a chat conversation, used for both input and output.

**Attributes:**

- `role` (str): The role of the author of this message (e.g., `"user"`, `"assistant"`, `"system"`, `"tool"`).
- `content` (Optional[str]): The content of the message.
- `function_call` (Optional[FunctionCall]): (Deprecated) The name and arguments of a function that should be called, as generated by the model. Use `tool_calls` instead.
- `tool_calls` (Optional[List[ToolCall]]): A list of tool calls generated by the model, if the model decided to call a tool.

### `ChoiceDelta`

Represents a partial message delta in a streaming chat completion. Only the fields that have changed are present.

**Attributes:**

- `content` (Optional[str]): The partial content of the message.
- `function_call` (Optional[FunctionCall]): (Deprecated) The name and arguments of a function that should be called. Use `tool_calls` instead.
- `role` (Optional[str]): The role of the author of this message.
- `tool_calls` (Optional[List[ToolCall]]): A list of tool calls generated by the model.

### `CompletionUsage`

Provides information about the token usage for a chat completion.

**Attributes:**

- `completion_tokens` (int): The number of tokens generated in the completion.
- `prompt_tokens` (int): The number of tokens in the input prompt.
- `total_tokens` (int): The total number of tokens used (prompt + completion).
- `prompt_tokens_details` (Optional[Dict[str, Any]]): Detailed breakdown of prompt token usage, if available.

### `Model`

Represents an AI model available through the HelpingAI API.

**Attributes:**

- `id` (str): The unique identifier of the model.
- `name` (str): The human-readable name of the model.
- `version` (Optional[str]): The version of the model, if applicable.
- `description` (Optional[str]): A brief description of the model's capabilities.
- `object` (str): The type of object, always `"model"`.

### `FunctionCall`

Represents a function call generated by the model. This is part of the deprecated `function_call` field in `ChatCompletionMessage` and `ChoiceDelta`.

**Attributes:**

- `name` (str): The name of the function to call.
- `arguments` (str): The arguments to the function, represented as a JSON string.

### `ToolFunction`

Represents the function details within a `ToolCall` object with enhanced execution capabilities.

**Attributes:**

- `name` (str): The name of the function to call.
- `arguments` (str): The arguments to the function, represented as a JSON string.

**Methods:**

- [`get_parsed_arguments()`](HelpingAI/base_models.py:123) `-> Dict[str, Any]`: Parses the `arguments` JSON string into a Python dictionary. Raises `ValueError` if the arguments are not valid JSON.

  ```python
  tool_call = response.choices[0].message.tool_calls[0]
  args = tool_call.function.get_parsed_arguments()
  print(f"Tool: {tool_call.function.name}, Args: {args}")
  ```

- [`call_with_registry(registry=None)`](HelpingAI/base_models.py:137) `-> Any`: Executes the function using a tool registry lookup. If `registry` is `None`, it uses the global tool registry. Raises an exception if the tool is not found or execution fails.

  ```python
  # Execute tool call using registry
  result = tool_call.function.call_with_registry()
  
  # Or with custom registry
  from HelpingAI.tools import ToolRegistry
  custom_registry = ToolRegistry()
  result = tool_call.function.call_with_registry(custom_registry)
  ```

- [`execute(registry=None)`](HelpingAI/base_models.py:167) `-> Any`: Alias for [`call_with_registry()`](HelpingAI/base_models.py:137) for convenience.

**Enhanced Tool Execution Example:**

```python
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Calculate 2+2 using Python"}],
    tools=["code_interpreter"]
)

# Get the tool call from response
tool_call = response.choices[0].message.tool_calls[0]

# Parse arguments
args = tool_call.function.get_parsed_arguments()
print(f"Calling {tool_call.function.name} with: {args}")

# Execute the tool call
result = tool_call.function.execute()
print(f"Result: {result}")
```

### `ToolCall`

Represents a single tool call generated by the model.

**Attributes:**

- `id` (str): A unique identifier for this tool call.
- `type` (str): The type of the tool call, currently always `"function"`.
- `function` (ToolFunction): A `ToolFunction` object containing the details of the function to be called.

## Error Handling

The HelpingAI SDK provides a robust error handling mechanism, raising specific exceptions for different types of API errors. All custom exceptions are subclasses of `HAIError`, allowing for granular error management.

### `HAIError`

Base exception class for all HelpingAI API errors. All other custom exceptions inherit from this class.

**Attributes:**

- `message` (str): A human-readable error message.
- `status_code` (Optional[int]): The HTTP status code of the response, if available.
- `headers` (Optional[Dict[str, Any]]): The HTTP response headers, if available.
- `body` (Optional[Dict[str, Any]]): The raw response body, if available.

### `AuthenticationError`

Raised when API key authentication fails. This is a subclass of `HAIError`.

### `NoAPIKeyError`

Raised specifically when no API key is provided during client initialization or found in the `HAI_API_KEY` environment variable. This is a subclass of `AuthenticationError`.

### `InvalidAPIKeyError`

Raised when the provided API key is invalid or has expired. This is a subclass of `AuthenticationError`.

### `PermissionDeniedError`

Raised when the API key does not have the necessary permissions for the requested operation. This is a subclass of `AuthenticationError`.

### `InvalidRequestError`

Raised when the request parameters are invalid (e.g., incorrect format, missing required fields). This is a subclass of `HAIError`.

**Attributes:**

- `param` (Optional[str]): The name of the parameter that caused the error, if applicable.
- `code` (Optional[str]): A specific error code, if provided by the API.

### `InvalidModelError`

Raised when an invalid or non-existent model ID is specified in the request. This is a subclass of `InvalidRequestError`.

### `RateLimitError`

Raised when the API rate limit for your account or organization has been exceeded. This is a subclass of `HAIError`.

**Attributes:**

- `retry_after` (Optional[int]): The number of seconds to wait before retrying the request, as indicated by the `Retry-After` header.

### `TooManyRequestsError`

Raised when too many requests are made within a short time window, indicating a rate limit issue. This is a subclass of `RateLimitError`.

### `ServiceUnavailableError`

Raised when the HelpingAI API service is temporarily unavailable due to maintenance or high load. This is a subclass of `HAIError`.

### `TimeoutError`

Raised when an API request times out, meaning the server did not respond within the specified `timeout` duration. This is a subclass of `HAIError`.

### `APIConnectionError`

Raised when there are network-related issues preventing a connection to the HelpingAI API (e.g., DNS resolution failure, network unreachable). This is a subclass of `HAIError`.

**Attributes:**

- `should_retry` (bool): Indicates whether the request can be safely retried.

### `APIError`

A generic API error that is raised for unhandled or unexpected API responses. This is a subclass of `HAIError`.

**Attributes:**

- `code` (Optional[str]): A specific error code, if provided by the API.
- `type` (Optional[str]): The type of error, if provided by the API.

### `ServerError`

Raised when the API server encounters an internal error. This is a subclass of `APIError`.

### `ContentFilterError`

Raised when the content of the request or response is flagged by moderation filters. This is a subclass of `InvalidRequestError`.

### `TokenLimitError`

Raised when the token limit for the request (prompt + completion) is exceeded. This is a subclass of `InvalidRequestError`.

### `InvalidContentError`

Raised when the provided content in the request is invalid or malformed. This is a subclass of `InvalidRequestError`.

## Tool-Specific Errors

These exceptions are specific to the tool calling functionality.

### `ToolExecutionError`

Raised when an error occurs during the execution of a tool's function. This is a subclass of [`HAIError`](HelpingAI/error.py:7).

**Attributes:**

- `tool_name` (Optional[str]): The name of the tool that failed to execute.
- `original_error` (Optional[Exception]): The original exception that caused the tool execution to fail.
- `message` (str): Human-readable error message describing the failure.

**Usage Example:**

```python
try:
    result = client.call("code_interpreter", {"code": "invalid python code"})
except ToolExecutionError as e:
    print(f"Tool execution failed: {e.message}")
    print(f"Failed tool: {e.tool_name}")
    if e.original_error:
        print(f"Original error: {e.original_error}")
```

### `SchemaValidationError`

Raised when a tool's schema is invalid or when arguments provided to a tool do not conform to its defined schema. This is a subclass of [`HAIError`](HelpingAI/error.py:7).

**Attributes:**

- `schema` (Optional[dict]): The schema that failed validation.
- `value` (Optional[Any]): The value that failed against the schema.
- `message` (str): Human-readable error message describing the validation failure.

**Usage Example:**

```python
try:
    # Invalid arguments for web_search (missing required 'query')
    result = client.call("web_search", {"max_results": 5})
except SchemaValidationError as e:
    print(f"Schema validation failed: {e.message}")
    print(f"Failed schema: {e.schema}")
    print(f"Invalid value: {e.value}")
```

### `ToolRegistrationError`

Raised when there is an issue registering a tool with the SDK's tool registry. This is a subclass of [`HAIError`](HelpingAI/error.py:7).

**Attributes:**

- `tool_name` (Optional[str]): The name of the tool that failed to register.
- `message` (str): Human-readable error message describing the registration failure.

**Usage Example:**

```python
try:
    from HelpingAI.tools import register_tool
    
    @register_tool
    def invalid_tool():
        pass  # Missing required schema information
        
except ToolRegistrationError as e:
    print(f"Tool registration failed: {e.message}")
    print(f"Failed tool: {e.tool_name}")
```

### `SchemaGenerationError`

Raised when the automatic schema generation from a Python function fails (e.g., due to unsupported type hints). This is a subclass of [`HAIError`](HelpingAI/error.py:7).

**Attributes:**

- `function_name` (Optional[str]): The name of the function for which schema generation failed.
- `type_hint` (Optional[Any]): The specific type hint that caused the generation error.
- `message` (str): Human-readable error message describing the schema generation failure.

**Usage Example:**

```python
try:
    from HelpingAI.tools import Fn
    
    def complex_function(arg: SomeUnsupportedType) -> ComplexReturnType:
        pass
    
    # This might fail if type hints are not supported
    fn_tool = Fn.from_function(complex_function)
    
except SchemaGenerationError as e:
    print(f"Schema generation failed: {e.message}")
    print(f"Function: {e.function_name}")
    print(f"Problematic type hint: {e.type_hint}")
```

## Error Handling Best Practices

**Comprehensive Error Handling:**

```python
from HelpingAI import HAI
from HelpingAI.error import (
    HAIError, AuthenticationError, InvalidRequestError,
    RateLimitError, APIConnectionError
)
from HelpingAI.tools.errors import ToolExecutionError

client = HAI()

try:
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "Hello!"}],
        tools=["code_interpreter"]
    )
    
    # Execute tool calls if present
    if response.choices[0].message.tool_calls:
        results = client.chat.completions.execute_tool_calls(
            response.choices[0].message
        )
        
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Handle API key issues
    
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
    if hasattr(e, 'param') and e.param:
        print(f"Problem with parameter: {e.param}")
    # Handle parameter validation issues
    
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    if hasattr(e, 'retry_after') and e.retry_after:
        print(f"Retry after {e.retry_after} seconds")
    # Handle rate limiting with backoff
    
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
    print(f"Failed tool: {e.tool_name}")
    # Handle tool-specific errors
    
except APIConnectionError as e:
    print(f"Connection error: {e}")
    if hasattr(e, 'should_retry') and e.should_retry:
        print("This error can be retried")
    # Handle network issues
    
except HAIError as e:
    print(f"General HAI error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Headers: {e.headers}")
    # Handle any other HAI-specific errors
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```