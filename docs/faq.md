# Frequently Asked Questions (FAQ)

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [Authentication](#authentication)
- [API Usage](#api-usage)
- [Models & Features](#models--features)
- [Error Handling](#error-handling)
- [Performance & Optimization](#performance--optimization)
- [Billing & Usage](#billing--usage)
- [Troubleshooting](#troubleshooting)

## General Questions

### What is HelpingAI?

HelpingAI is an advanced AI platform that specializes in emotional intelligence. Our models are designed to understand, process, and respond to human emotions with exceptional accuracy and empathy. The platform offers AI models that excel at:

- Emotional understanding and recognition
- Empathetic communication
- Psychological insights
- Therapeutic and supportive interactions
- Educational content about emotional intelligence

### How is HelpingAI different from other AI platforms?

HelpingAI focuses specifically on emotional intelligence, making our models uniquely suited for:
- Mental health and wellness applications
- Educational tools for emotional learning
- Customer service with empathetic responses
- Personal development and coaching
- Therapeutic and counseling support

### What can I build with HelpingAI?

Popular applications include:
- Emotional support chatbots
- Mental health screening tools
- Educational platforms for EQ development
- Customer service with emotional awareness
- Content analysis for emotional tone
- Personal coaching and development apps
- Therapeutic conversation partners

## Installation & Setup

### How do I install the HelpingAI Python SDK?

```bash
pip install HelpingAI
```

### What are the system requirements?

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, Linux
- **Dependencies**: `requests`, `typing_extensions` (automatically installed)

### How do I upgrade to the latest version?

```bash
pip install --upgrade HelpingAI
```

### Can I use this in a virtual environment?

Yes, and it's recommended:

```bash
# Create virtual environment
python -m venv helpingai_env

# Activate it
# On Windows:
helpingai_env\Scripts\activate
# On macOS/Linux:
source helpingai_env/bin/activate

# Install HelpingAI
pip install HelpingAI
```

## Authentication

### How do I get an API key?

1. Visit [helpingai.co/dashboard](https://helpingai.co/dashboard)
2. Sign up or log in to your account
3. Navigate to the API Keys section
4. Generate a new API key
5. Copy and securely store your key

### How do I set up authentication?

**Method 1: Environment Variable (Recommended)**
```bash
export HAI_API_KEY='your-api-key-here'
```

**Method 2: Direct in Code**
```python
from HelpingAI import HAI
hai = HAI(api_key='your-api-key-here')
```

### Why am I getting authentication errors?

Common causes:
- **Invalid API key**: Check if your key is correct
- **Expired key**: Generate a new key in the dashboard
- **Incorrect environment variable**: Ensure `HAI_API_KEY` is set correctly
- **Account issues**: Verify your account status in the dashboard

### How do I rotate my API keys?

1. Generate a new key in the dashboard
2. Update your environment variables or code
3. Test with the new key
4. Delete the old key from the dashboard

### Can I use multiple API keys?

Yes, you can create multiple clients:

```python
client1 = HAI(api_key='key-1')
client2 = HAI(api_key='key-2')
```

## API Usage

### What models are available?

We offer two powerful models:

**Dhanishtha-2.0-preview** - Advanced Emotional Intelligence:
- Enhanced emotional understanding and contextual awareness
- Trained on 15M emotional dialogues and 3M therapeutic exchanges
- Best for emotional support, therapy guidance, and personalized learning

**Dhanishtha-2.0-preview** - Revolutionary Reasoning Model:
- World's first intermediate thinking model with multi-phase reasoning
- Features transparent `<think>...</think>` blocks and self-correction
- Best for complex problem-solving and analytical tasks

List all available models:
```python
models = hai.models.list()
for model in models:
    print(model.id)
```

### How do I make my first API call?

```python
from HelpingAI import HAI

hai = HAI()
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### What's the difference between streaming and non-streaming?

**Non-streaming**: Get the complete response at once
```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Hello"}],
    stream=False  # Default
)
```

**Streaming**: Get response in real-time chunks
```python
for chunk in hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### How do I maintain conversation context?

Keep message history:

```python
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is empathy?"}
]

response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=conversation
)

# Add AI response to history
conversation.append({
    "role": "assistant",
    "content": response.choices[0].message.content
})

# Continue conversation
conversation.append({
    "role": "user",
    "content": "How can I develop empathy?"
})
```

### What parameters can I adjust?

Key parameters:

| Parameter | Range | Purpose | Recommended |
|-----------|-------|---------|-------------|
| `temperature` | 0.0-1.0 | Controls creativity | 0.7 for creative, 0.3 for factual |
| `max_tokens` | 1-4096 | Response length | 500-1000 for conversations |
| `top_p` | 0.0-1.0 | Nucleus sampling | 0.9 for most cases |
| `frequency_penalty` | -2.0-2.0 | Reduces repetition | 0.3 for variety |
| `presence_penalty` | -2.0-2.0 | Encourages new topics | 0.3 for diversity |

## Models & Features

### What is the `hide_think` parameter?

The `hide_think` parameter filters out internal reasoning blocks (`<think>` and `<ser>` tags) from responses:

```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Explain empathy"}],
    hide_think=True  # Cleaner output
)
```

### How do I get the best emotional intelligence responses?

1. **Use clear system messages**:
```python
{"role": "system", "content": "You are an expert in emotional intelligence and psychology."}
```

2. **Provide context**:
```python
{"role": "user", "content": "I'm feeling overwhelmed at work. Can you help me understand what I'm experiencing and how to cope?"}
```

3. **Use appropriate temperature** (0.6-0.8 for empathetic responses)

### Can I use function calling or tools?

Yes, the SDK supports OpenAI-compatible function calling:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_emotion",
            "description": "Analyze emotional content",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "context": {"type": "string"}
                }
            }
        }
    }
]

response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Analyze this text for emotions"}],
    tools=tools,
    tool_choice="auto"
)
```

## Error Handling

### What errors might I encounter?

Common error types:

- **`NoAPIKeyError`**: No API key provided
- **`InvalidAPIKeyError`**: Invalid or expired API key
- **`RateLimitError`**: Too many requests
- **`InvalidRequestError`**: Invalid parameters
- **`ServiceUnavailableError`**: API temporarily unavailable
- **`TimeoutError`**: Request timed out

### How do I handle rate limits?

```python
from HelpingAI import RateLimitError
import time

try:
    response = hai.chat.completions.create(...)
except RateLimitError as e:
    print(f"Rate limited. Waiting {e.retry_after} seconds...")
    time.sleep(e.retry_after or 60)
    # Retry the request
```

### What's the best way to implement retry logic?

```python
def robust_completion(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=messages
            )
        except RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(e.retry_after or (2 ** attempt))
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
```

### How do I debug API issues?

1. **Enable logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Check response details**:
```python
try:
    response = hai.chat.completions.create(...)
except HAIError as e:
    print(f"Status: {e.status_code}")
    print(f"Headers: {e.headers}")
    print(f"Body: {e.body}")
```

3. **Validate your request**:
```python
# Check message format
messages = [{"role": "user", "content": "Hello"}]
assert all("role" in msg and "content" in msg for msg in messages)
```

## Performance & Optimization

### How can I optimize API usage?

1. **Reuse client instances**:
```python
# Good
hai = HAI()
for message in messages:
    response = hai.chat.completions.create(...)

# Avoid
for message in messages:
    hai = HAI()  # Don't create new clients
    response = hai.chat.completions.create(...)
```

2. **Use appropriate timeouts**:
```python
hai = HAI(timeout=30.0)  # 30 second timeout
```

3. **Implement caching for repeated requests**:
```python
cache = {}
def cached_completion(messages, cache_key):
    if cache_key in cache:
        return cache[cache_key]
    response = hai.chat.completions.create(...)
    cache[cache_key] = response
    return response
```

### How do I handle high-volume requests?

1. **Implement rate limiting**:
```python
import time
def rate_limited_requests(requests, delay=1.0):
    for i, request in enumerate(requests):
        response = hai.chat.completions.create(**request)
        if i < len(requests) - 1:
            time.sleep(delay)
        yield response
```

2. **Use batch processing**:
```python
def process_batch(message_lists, batch_size=10):
    for i in range(0, len(message_lists), batch_size):
        batch = message_lists[i:i+batch_size]
        for messages in batch:
            yield hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=messages
            )
        time.sleep(1)  # Pause between batches
```

### What's the recommended timeout setting?

- **Short requests**: 15-30 seconds
- **Long conversations**: 60-120 seconds
- **Streaming**: 30-60 seconds

```python
hai = HAI(timeout=60.0)  # 60 second timeout
```

## Billing & Usage

### How is usage calculated?

Usage is calculated based on **output tokens only**. You are not charged for input tokens. Monitor usage in your dashboard at [helpingai.co/dashboard](https://helpingai.co/dashboard).

### How can I monitor token usage?

```python
response = hai.chat.completions.create(...)
if response.usage:
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
```

### How can I control costs?

1. **Set max_tokens limits**:
```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    max_tokens=200  # Limit response length
)
```

2. **Use lower temperature for consistent results**:
```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    temperature=0.3  # More predictable, potentially shorter responses
)
```

3. **Implement usage tracking**:
```python
class UsageTracker:
    def __init__(self):
        self.total_tokens = 0
    
    def track_completion(self, response):
        if response.usage:
            self.total_tokens += response.usage.total_tokens
        return response

tracker = UsageTracker()
response = hai.chat.completions.create(...)
tracker.track_completion(response)
```

### Are there usage limits?

Check your current limits in the dashboard. Limits vary by plan:
- **Free tier**: Limited requests per month
- **Paid plans**: Higher limits based on subscription

## Troubleshooting

### My requests are timing out. What should I do?

1. **Increase timeout**:
```python
hai = HAI(timeout=120.0)  # 2 minutes
```

2. **Reduce request complexity**:
```python
# Shorter messages
messages = [{"role": "user", "content": "Brief question here"}]

# Lower max_tokens
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    max_tokens=200
)
```

3. **Use streaming for long responses**:
```python
for chunk in hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    stream=True
):
    # Process chunks as they arrive
```

### I'm getting inconsistent responses. How can I make them more consistent?

1. **Lower temperature**:
```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    temperature=0.2  # More deterministic
)
```

2. **Use seed for reproducibility**:
```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    seed=42  # Same seed = same response
)
```

3. **Provide clearer instructions**:
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant. Always provide structured, consistent responses."},
    {"role": "user", "content": "Please explain empathy in exactly 3 bullet points."}
]
```

### The SDK is not working in my environment. What should I check?

1. **Python version**:
```bash
python --version  # Should be 3.7+
```

2. **Installation**:
```bash
pip show HelpingAI
pip install --upgrade HelpingAI
```

3. **Dependencies**:
```bash
pip install requests typing_extensions
```

4. **Network connectivity**:
```python
import requests
response = requests.get("https://api.helpingai.co/v1/models")
print(response.status_code)  # Should be 200
```

5. **Environment variables**:
```python
import os
print(os.getenv("HAI_API_KEY"))  # Should show your key
```

### How do I report bugs or request features?

1. **GitHub Issues**: [github.com/HelpingAI/HelpingAI-python/issues](https://github.com/HelpingAI/HelpingAI-python/issues)
2. **Email Support**: varun@helpingai.co
3. **Documentation**: [helpingai.co/docs](https://helpingai.co/docs)

When reporting issues, please include:
- Python version
- SDK version (`pip show HelpingAI`)
- Error messages and stack traces
- Minimal code to reproduce the issue
- Expected vs. actual behavior

### Where can I find more help?

- **Documentation**: [Getting Started](getting_started.md), [API Reference](api_reference.md), [Examples](examples.md)
- **Dashboard**: [helpingai.co/dashboard](https://helpingai.co/dashboard)
- **Community**: GitHub Discussions
- **Support**: helpingaiemotional@gmail.com

---

**Still have questions?** Don't hesitate to reach out to our support team at helpingaiemotional@gmail.com or create an issue on GitHub. We're here to help you build amazing applications with emotional intelligence! 🚀
## Too
l Calling Framework

### How do I create a tool for AI to use?

The easiest way is to use the `@tools` decorator:

```python
from HelpingAI.tools import tools

@tools
def get_weather(city: str, units: str = "celsius") -> dict:
    """Get weather information for a city.
    
    Args:
        city: City name to get weather for
        units: Temperature units (celsius or fahrenheit)
    """
    # Your implementation here
    return {"temperature": 22, "units": units, "city": city}
```

### How do I use tools with chat completions?

Use the `get_tools()` function to include all registered tools:

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools

hai = HAI()
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=get_tools(),
    tool_choice="auto"
)
```

### How do I handle tool calls in the response?

Check for tool calls in the response and execute them:

```python
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    # Get the tool from registry
    from HelpingAI.tools import get_registry
    tool = get_registry().get_tool(function_name)
    
    # Execute the tool
    result = tool.call(function_args)
    
    # Continue the conversation with the tool result
    follow_up = hai.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            # Previous messages...
            response.choices[0].message,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result)
            }
        ]
    )
```

### Can I combine my tools with existing OpenAI-format tools?

Yes, use the `merge_tool_lists` function:

```python
from HelpingAI.tools import merge_tool_lists, get_tools

# Existing OpenAI-format tools
legacy_tools = [{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}]

# Combine with your @tools functions
combined_tools = merge_tool_lists(
    legacy_tools,
    get_tools()
)

# Use in chat completion
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Help me with this"}],
    tools=combined_tools
)
```

### How do I handle errors in tool execution?

Use try/except blocks with the specific error types:

```python
from HelpingAI.tools import ToolExecutionError, SchemaValidationError

try:
    result = tool.call(arguments)
except SchemaValidationError as e:
    print(f"Invalid arguments: {e}")
    # Handle invalid arguments
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
    # Handle execution failure
```

### How do I create tools with complex parameter types?

The `@tools` decorator supports various Python type hints:

```python
from typing import List, Optional, Union, Literal
from enum import Enum

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@tools
def create_task(
    title: str,
    description: Optional[str] = None,
    priority: Priority = Priority.MEDIUM,
    tags: List[str] = None,
    due_date: Union[str, None] = None,
    status: Literal["todo", "in_progress", "done"] = "todo"
) -> dict:
    """Create a new task."""
    # Implementation
    return {"title": title, "status": "created"}
```