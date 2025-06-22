# API Reference

Complete reference documentation for the HelpingAI Python SDK.

## Table of Contents

- [HAI Client](#hai-client)
- [Chat Completions](#chat-completions)
- [Models](#models)
- [Response Objects](#response-objects)
- [Error Handling](#error-handling)
- [Type Definitions](#type-definitions)

## HAI Client

### Class: `HAI`

The main client class for interacting with the HelpingAI API.

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

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `Optional[str]` | `None` | Your API key. If not provided, reads from `HAI_API_KEY` environment variable |
| `organization` | `Optional[str]` | `None` | Optional organization ID for API requests |
| `base_url` | `Optional[str]` | `"https://api.helpingai.co/v1"` | Base URL for API requests |
| `timeout` | `float` | `60.0` | Request timeout in seconds |

**Properties:**

- `chat`: Access to chat completions API
- `models`: Access to models API

**Example:**

```python
from HelpingAI import HAI

# Using environment variable
hai = HAI()

# With explicit API key
hai = HAI(api_key="your-api-key")

# With custom configuration
hai = HAI(
    api_key="your-api-key",
    timeout=30.0,
    organization="your-org-id"
)
```

## Chat Completions

### Method: `chat.completions.create`

Create a chat completion request.

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

**Required Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `str` | Model ID to use (e.g., "Helpingai3-raw", "Dhanishtha-2.0-preview") |
| `messages` | `List[Dict[str, str]]` | List of message objects with "role" and "content" |

**Optional Parameters:**

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `temperature` | `float` | 0.0-1.0 | `None` | Controls randomness in responses |
| `max_tokens` | `int` | 1-4096 | `None` | Maximum tokens to generate |
| `top_p` | `float` | 0.0-1.0 | `None` | Nucleus sampling parameter |
| `frequency_penalty` | `float` | -2.0-2.0 | `None` | Penalizes frequent tokens |
| `presence_penalty` | `float` | -2.0-2.0 | `None` | Penalizes repeated topics |
| `stop` | `Union[str, List[str]]` | - | `None` | Stop sequences |
| `stream` | `bool` | - | `False` | Enable streaming responses |
| `user` | `str` | - | `None` | User identifier for tracking |
| `n` | `int` | 1-10 | `None` | Number of completions to generate |
| `logprobs` | `bool` | - | `None` | Include log probabilities |
| `top_logprobs` | `int` | 0-20 | `None` | Number of top log probabilities |
| `response_format` | `Dict[str, str]` | - | `None` | Response format specification |
| `seed` | `int` | - | `None` | Random seed for deterministic results |
| `tools` | `List[Dict[str, Any]]` | - | `None` | Tool/function definitions |
| `tool_choice` | `Union[str, Dict[str, Any]]` | - | `"auto"` | Tool selection strategy |
| `hide_think` | `bool` | - | `False` | Filter out reasoning blocks |

**Returns:**

- If `stream=False`: `ChatCompletion` object
- If `stream=True`: `Iterator[ChatCompletionChunk]`

**Examples:**

```python
# Basic completion
response = hai.chat.completions.create(
    model="Helpingai3-raw",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

# Advanced completion with parameters
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a poem"}
    ],
    temperature=0.8,
    max_tokens=200,
    top_p=0.9,
    frequency_penalty=0.3,
    presence_penalty=0.3,
    hide_think=True
)

# Streaming completion
for chunk in hai.chat.completions.create(
    model="Helpingai3-raw",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Models

### Method: `models.list`

List all available models.

```python
def list() -> List[Model]
```

**Returns:** List of `Model` objects

**Example:**

```python
models = hai.models.list()
for model in models:
    print(f"ID: {model.id}, Name: {model.name}")
```

### Method: `models.retrieve`

Retrieve information about a specific model.

```python
def retrieve(model_id: str) -> Model
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `model_id` | `str` | The ID of the model to retrieve |

**Returns:** `Model` object

**Example:**

```python
model = hai.models.retrieve("Helpingai3-raw")
print(f"Model: {model.name}")
```

## Response Objects

### ChatCompletion

Response object for non-streaming completions.

```python
@dataclass
class ChatCompletion:
    id: str                           # Unique identifier
    created: int                      # Unix timestamp
    model: str                        # Model used
    choices: List[Choice]             # List of completion choices
    usage: Optional[CompletionUsage]  # Token usage information
    system_fingerprint: Optional[str] # System fingerprint
```

**Example:**

```python
response = hai.chat.completions.create(...)
print(f"ID: {response.id}")
print(f"Model: {response.model}")
print(f"Content: {response.choices[0].message.content}")
if response.usage:
    print(f"Total tokens: {response.usage.total_tokens}")
```

### ChatCompletionChunk

Response object for streaming completions.

```python
@dataclass
class ChatCompletionChunk:
    id: str                           # Unique identifier
    created: int                      # Unix timestamp
    model: str                        # Model used
    choices: List[Choice]             # List of completion choices
    system_fingerprint: Optional[str] # System fingerprint
```

### Choice

Individual completion choice.

```python
@dataclass
class Choice:
    index: int                        # Choice index
    message: Optional[ChatCompletionMessage]  # Complete message (non-streaming)
    delta: Optional[ChoiceDelta]      # Message delta (streaming)
    finish_reason: Optional[str]      # Reason for completion end
    logprobs: Optional[Any]           # Log probabilities
```

**Finish Reasons:**

- `"stop"`: Natural completion
- `"length"`: Maximum token limit reached
- `"content_filter"`: Content filtered
- `"tool_calls"`: Tool/function call made

### ChatCompletionMessage

Complete message object.

```python
@dataclass
class ChatCompletionMessage:
    role: str                         # "assistant", "user", "system"
    content: Optional[str]            # Message content
    function_call: Optional[FunctionCall]  # Function call (deprecated)
    tool_calls: Optional[List[ToolCall]]   # Tool calls
```

### ChoiceDelta

Message delta for streaming.

```python
@dataclass
class ChoiceDelta:
    content: Optional[str]            # Content delta
    role: Optional[str]               # Role (first chunk only)
    function_call: Optional[FunctionCall]  # Function call delta
    tool_calls: Optional[List[ToolCall]]   # Tool call deltas
```

### CompletionUsage

Token usage information.

```python
@dataclass
class CompletionUsage:
    completion_tokens: int            # Tokens in completion
    prompt_tokens: int                # Tokens in prompt
    total_tokens: int                 # Total tokens used
```

### Model

Model information object.

```python
@dataclass
class Model:
    id: str                           # Model identifier
    name: str                         # Model name
    version: Optional[str]            # Model version
    description: Optional[str]        # Model description
    object: str                       # Object type ("model")
```

## Error Handling

### Exception Hierarchy

```
HAIError (base)
├── AuthenticationError
│   ├── NoAPIKeyError
│   ├── InvalidAPIKeyError
│   └── PermissionDeniedError
├── InvalidRequestError
│   ├── InvalidModelError
│   ├── ContentFilterError
│   ├── TokenLimitError
│   └── InvalidContentError
├── RateLimitError
│   └── TooManyRequestsError
├── APIError
│   └── ServerError
├── ServiceUnavailableError
├── TimeoutError
└── APIConnectionError
```

### HAIError (Base Exception)

```python
class HAIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    )
```

**Attributes:**

- `message`: Error message
- `status_code`: HTTP status code
- `headers`: Response headers
- `body`: Response body

### Specific Exceptions

#### AuthenticationError

Authentication-related errors.

```python
# No API key provided
raise NoAPIKeyError()

# Invalid API key
raise InvalidAPIKeyError(status_code=401, headers={})

# Permission denied
raise PermissionDeniedError("Insufficient permissions")
```

#### InvalidRequestError

Request validation errors.

```python
# Invalid model
raise InvalidModelError("gpt-4", status_code=400)

# Content filtered
raise ContentFilterError("Content violates policy")

# Token limit exceeded
raise TokenLimitError("Request too long")
```

#### RateLimitError

Rate limiting errors.

```python
# Rate limit exceeded
raise RateLimitError("Rate limit exceeded", retry_after=60)

# Too many requests
raise TooManyRequestsError(status_code=429)
```

**Special Attributes:**

- `retry_after`: Seconds to wait before retrying

#### APIError

Generic API errors.

```python
# Server error
raise ServerError("Internal server error", status_code=500)

# Generic API error
raise APIError("Unknown error", code="unknown", type="api_error")
```

#### ServiceUnavailableError

Service availability errors.

```python
raise ServiceUnavailableError(status_code=503)
```

#### TimeoutError

Request timeout errors.

```python
raise TimeoutError("Request timed out")
```

#### APIConnectionError

Connection-related errors.

```python
raise APIConnectionError("Connection failed", should_retry=True)
```

**Special Attributes:**

- `should_retry`: Whether the request should be retried

### Error Handling Examples

```python
from HelpingAI import (
    HAI, HAIError, RateLimitError, InvalidRequestError,
    AuthenticationError, ServiceUnavailableError, TimeoutError
)
import time

def handle_completion_errors():
    try:
        response = hai.chat.completions.create(
            model="Helpingai3-raw",
            messages=[{"role": "user", "content": "Hello"}]
        )
        return response
        
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
        time.sleep(e.retry_after or 60)
        # Retry logic here
        
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        # Handle auth error (don't retry)
        
    except InvalidRequestError as e:
        print(f"Invalid request: {e}")
        if hasattr(e, 'param'):
            print(f"Parameter: {e.param}")
        # Handle validation error
        
    except ServiceUnavailableError as e:
        print("Service temporarily unavailable")
        # Implement backoff and retry
        
    except TimeoutError as e:
        print("Request timed out")
        # Handle timeout
        
    except HAIError as e:
        print(f"API error: {e}")
        print(f"Status code: {e.status_code}")
        # Handle generic API error
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle unexpected errors
```

## Type Definitions

### Message Types

```python
from typing import Dict, List, Optional, Union, Any, Iterator

# Message dictionary
MessageDict = Dict[str, str]  # {"role": "user", "content": "Hello"}

# Message list
MessageList = List[MessageDict]

# Tool definition
ToolDict = Dict[str, Any]

# Response format
ResponseFormatDict = Dict[str, str]
```

### Common Type Aliases

```python
# Model identifier
ModelId = str

# Token count
TokenCount = int

# Temperature value
Temperature = float  # 0.0 to 1.0

# Penalty value
Penalty = float  # -2.0 to 2.0

# Stop sequences
StopSequences = Union[str, List[str]]

# Tool choice
ToolChoice = Union[str, Dict[str, Any]]
```

### Function Signatures

```python
# Chat completion function
def create_completion(
    model: ModelId,
    messages: MessageList,
    temperature: Optional[Temperature] = None,
    max_tokens: Optional[TokenCount] = None,
    # ... other parameters
) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
    ...

# Model listing function
def list_models() -> List[Model]:
    ...

# Model retrieval function
def retrieve_model(model_id: ModelId) -> Model:
    ...
```

## Usage Examples

### Complete Example

```python
from HelpingAI import HAI, HAIError
import os

# Initialize client
hai = HAI(api_key=os.getenv("HAI_API_KEY"))

try:
    # List available models
    models = hai.models.list()
    print(f"Available models: {[m.id for m in models]}")
    
    # Create completion
    response = hai.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing"}
        ],
        temperature=0.7,
        max_tokens=500,
        hide_think=True
    )
    
    # Process response
    message = response.choices[0].message
    print(f"Response: {message.content}")
    
    # Check usage
    if response.usage:
        print(f"Tokens used: {response.usage.total_tokens}")
        
except HAIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Streaming Example

```python
def stream_completion(prompt: str):
    try:
        stream = hai.chat.completions.create(
            model="Helpingai3-raw",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            hide_think=True
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
                
        return full_response
        
    except HAIError as e:
        print(f"Streaming error: {e}")
        return None

# Usage
response = stream_completion("Write a short poem about AI")
```

---

This completes the comprehensive API reference for the HelpingAI Python SDK. For more examples and use cases, see the [Examples](examples.md) documentation.