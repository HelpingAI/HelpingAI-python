# HelpingAI SDK Examples

Comprehensive examples for using the HelpingAI Python SDK.

## Installation

```bash
pip install helpingai
```

## Basic Usage

### Initialize Client

```python
from helpingai import HAI

# Initialize with API key
client = HAI(
    api_key="your-api-key",
    base_url="https://api.helpingai.co/v1"  # Optional: specify base URL
)

# Or use environment variable HAI_API_KEY
client = HAI()
```

### Chat Completions

```python
# Basic chat completion
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[
        {"role": "user", "content": "Hello! Can you help me understand emotional intelligence?"}
    ]
)
print(response.choices[0].message.content)

# With system message
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[
        {"role": "system", "content": "You are HelpingAI, an emotional AI."},
        {"role": "user", "content": "What are the key components of EQ?"}
    ]
)
```

### Streaming Responses

```python
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Explain mindfulness"}],
    stream=True
)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Models

```python
list = model = client.models.list()
print(list)

model = client.models.retrieve("HelpingAI2.5-10B")
print(model)

```

## Conversation Management

```python
# Initialize conversation with context
conversation = [
    {"role": "system", "content": "You are HelpingAI, an emotional AI."},
    {"role": "user", "content": "What is empathy?"}
]

# Get response
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=conversation
)

# Add response to conversation history
conversation.append({
    "role": "assistant",
    "content": response.choices[0].message.content
})

# Continue conversation
conversation.append({
    "role": "user",
    "content": "How can I improve my empathy?"
})

response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=conversation
)
```

## Parameter Control

```python
# Advanced parameter usage
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Write a story about empathy"}],
    temperature=0.7,        # Controls randomness (0-1)
    max_tokens=500,        # Maximum length of response
    top_p=0.9,            # Nucleus sampling parameter
    frequency_penalty=0.3, # Reduces repetition
    presence_penalty=0.3   # Encourages new topics
)
```

## Error Handling

```python
from helpingai import HAI, HAIError, RateLimitError, InvalidRequestError
import time

client = HAI()

def make_completion_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="HelpingAI2.5-10B",
                messages=messages
            )
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(e.retry_after)
        except InvalidRequestError as e:
            print(f"Invalid request: {str(e)}")
            raise
        except HAIError as e:
            print(f"API error: {str(e)}")
            raise

# Usage
try:
    response = make_completion_with_retry([
        {"role": "user", "content": "Hello"}
    ])
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Failed after retries: {str(e)}")
```

## Best Practices

### Environment Variables

```python
import os
from helpingai import HAI

# Set API key in environment
os.environ["HAI_API_KEY"] = "your-api-key"

# Initialize client using environment variable
client = HAI()
```

### Error Handling with Context Manager

```python
from contextlib import contextmanager
from helpingai import HAI, HAIError, RateLimitError

@contextmanager
def hai_context():
    try:
        yield
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
    except HAIError as e:
        print(f"API error: {str(e)}")

# Usage
client = HAI()
with hai_context():
    response = client.chat.completions.create(
        model="HelpingAI2.5-10B",
        messages=[{"role": "user", "content": "Hello"}]
    )
```

## Response Object Structure

```python
response = client.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Hello"}]
)

# Access response data
print(f"Response ID: {response.id}")
print(f"Model used: {response.model}")
print(f"Created timestamp: {response.created}")

# Access the message
message = response.choices[0].message
print(f"Role: {message.role}")
print(f"Content: {message.content}")

# Check token usage
if response.usage:
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
```
