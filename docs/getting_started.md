
# Getting Started with HelpingAI

Welcome to the HelpingAI Python library! This guide will help you install, authenticate, and make your first request using the library.

## Installation

You can install the HelpingAI library using pip:

```bash
pip install HelpingAI
```

## Authentication

To authenticate, you need your HelpingAI API key. You can obtain your API key from the [HelpingAI Dashboard](https://helpingai.co/dashboard).

### Setting the API Key via Environment Variable

Set the API key as an environment variable:

```bash
export HAI_API_KEY='your-api-key'
```

### Passing the API Key Explicitly

Alternatively, you can pass the API key when creating the client:

```python
from HelpingAI import HAI

hai = HAI(api_key='your-api-key')
```

## Making Your First Request

Here's a simple example to get you started:

```python
from HelpingAI import HAI

# Create the client instance (API key can be passed explicitly or through environment variables)
hai = HAI()

# Make a chat completion request
completion = hai.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[
        {"role": "user", "content": "Hello! How can you help me?"}
    ]
)

# Print the response from the AI
print(completion.choices[0].message.content)
```

## Working with Models

### Listing Available Models

```python
# List all available models
models = hai.models.list()
print([model.id for model in models])
```

### Retrieving a Specific Model

```python
# Retrieve details of a specific model
model = hai.models.retrieve("HelpingAI2.5-10B")
```

## Chat Completions

### Basic Completion Example

```python
completion = hai.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is emotional intelligence?"}
    ]
)

print(completion.choices[0].message.content)
```

### Streaming Completion Example

```python
# Example for streaming responses
for chunk in hai.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Completion Parameters

You can fine-tune the response with various parameters:

```python
completion = hai.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Write a poem"}],
    temperature=0.7,         # Controls randomness (0 to 1)
    max_tokens=100,          # Limits the response length
    top_p=0.9,               # Nucleus sampling parameter
    frequency_penalty=0.0,   # Reduces repetition (-2.0 to 2.0)
    presence_penalty=0.0     # Encourages topic changes (-2.0 to 2.0)
)
```

## Error Handling

The SDK provides specific exception types for handling different errors. Here's an example:

```python
from HelpingAI import HAI, HAIError, RateLimitError, InvalidRequestError

hai = HAI()

try:
    completion = hai.chat.completions.create(
        model="HelpingAI2.5-10B",
        messages=[{"role": "user", "content": "Hello"}]
    )
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except InvalidRequestError as e:
    print(f"Bad request: {str(e)}")
except HAIError as e:
    print(f"API error: {str(e)}")
```

## Advanced Configuration

You can configure additional settings (such as request timeouts) during client initialization:

```python
hai = HAI(
    api_key="your-api-key",
    timeout=30.0  # Request timeout in seconds
)
```

## Response Objects

### ChatCompletion Object

After making a request, the response object provides useful information:

```python
completion = hai.chat.completions.create(...)

print(completion.id)                  # Unique identifier for the response
print(completion.created)             # Unix timestamp of creation
print(completion.model)               # Model used for the request
print(completion.usage.total_tokens)  # Total tokens used in the request
```

### Message Object

Each completion contains a message object with details of the response:

```python
message = completion.choices[0].message

print(message.role)     # Typically "assistant"
print(message.content)  # The actual content of the response
```

## Best Practices

1. **Environment Variables**: Secure your API key by setting it as an environment variable.
2. **Error Handling**: Gracefully handle potential API errors.
3. **Resource Management**: Monitor token usage and implement rate limit handling.
4. **Timeouts**: Configure appropriate timeouts for your requests.

## Next Steps

- Refer to the [API Reference](api_reference.md) for detailed documentation on all available endpoints.
- Explore additional [Examples](examples.md) to see more advanced use cases.
- Check out the [FAQ](faq.md) for answers to common questions.



