# API Reference

Complete reference documentation for the HelpingAI Python SDK.

## HAI Class

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

The `HAI` class is the main interface to the HelpingAI API. It provides access to all API endpoints through its properties.

**Parameters**:

- `api_key`: Your API key. Find it at <https://helpingai.co/dashboard>
- `organization`: Optional organization ID for API requests
- `base_url`: Override the default API base URL
- `timeout`: Request timeout in seconds (default: 60.0)

## Chat Completions

### Create Completion

```python
HAI.chat.completions.create(
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
    tool_choice: Optional[Union[str, Dict[str, Any]]] = "auto"
)
```

Creates a chat completion request.

**Required Parameters**:

- `model`: ID of the model to use
- `messages`: List of messages in the conversation

**Optional Parameters**:

- `temperature`: Sampling temperature between 0 and 1
- `max_tokens`: Maximum number of tokens to generate
- `top_p`: Nucleus sampling parameter between 0 and 1
- `frequency_penalty`: Number between -2.0 and 2.0 to penalize token frequency
- `presence_penalty`: Number between -2.0 and 2.0 to penalize token presence
- `stop`: Sequence(s) at which to stop generation
- `stream`: Whether to stream responses
- `user`: Unique user identifier
- `n`: Number of chat completion choices
- `logprobs`: Include log probability information
- `top_logprobs`: Number of top log probability values to return
- `response_format`: Specifies the response format
- `seed`: Random number seed for deterministic results
- `tools`: List of tool configurations
- `tool_choice`: Strategy for tool handling (defaults to "auto")

**Returns**:

- If `stream=False`: `ChatCompletion` object
- If `stream=True`: Iterator of `ChatCompletionChunk` objects

## Models

### List Models

```python
HAI.models.list() -> List[Model]
```

Lists the currently available models.

### Retrieve Model

```python
HAI.models.retrieve(model_id: str) -> Model
```

Retrieves a model instance by ID.

**Parameters**:

- `model_id`: The ID of the model to retrieve

## Response Types

### ChatCompletion

```python
class ChatCompletion:
    id: str                      # Unique identifier
    created: int                 # Unix timestamp
    model: str                   # Model used
    choices: List[Choice]        # List of completion choices
    usage: Optional[Usage]       # Token usage information
```

### Choice

```python
class Choice:
    index: int                   # Choice index
    message: ChatMessage         # Generated message
    finish_reason: Optional[str] # Why generation stopped
```

### ChatMessage

```python
class ChatMessage:
    role: str                    # "assistant", "system", or "user"
    content: Optional[str]       # Message content
```

### Usage

```python
class Usage:
    completion_tokens: int       # Tokens in completion
    prompt_tokens: int          # Tokens in prompt
    total_tokens: int           # Total tokens used
```

## Error Types

### HAIError

Base exception class for all HelpingAI errors.

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

### Specific Error Types

The library provides several specific error types:

- `HAIError`: Base exception class
- `APIError`: Generic API errors
- `AuthenticationError`: API key or authentication issues
- `InvalidRequestError`: Invalid parameters or requests
- `RateLimitError`: Rate limit exceeded
- `ServiceUnavailableError`: API service unavailable
- `APIConnectionError`: Connection problems
- `TimeoutError`: Request timeout

## Basic Usage

```python
from helpingai import HAI

# Initialize the client
hai = HAI(api_key="your-api-key")

# Create a chat completion
response = hai.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Print the response
print(response.choices[0].message.content)
```
