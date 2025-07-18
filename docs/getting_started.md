# Getting Started with HelpingAI Python SDK

Welcome to the HelpingAI Python SDK! This comprehensive guide will help you install, authenticate, and start building with our emotionally intelligent AI models.

## 📦 Installation

Install the HelpingAI SDK using pip:

```bash
pip install HelpingAI
```

### System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, Linux
- **Dependencies**: Automatically installed with the package

## 🔑 Authentication

To use the HelpingAI API, you need an API key from the [HelpingAI Dashboard](https://helpingai.co/dashboard).

### Method 1: Environment Variable (Recommended)

Set your API key as an environment variable for security:

**Linux/macOS:**
```bash
export HAI_API_KEY='your-api-key-here'
```

**Windows (Command Prompt):**
```cmd
set HAI_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:HAI_API_KEY="your-api-key-here"
```

### Method 2: Direct Initialization

Pass the API key directly when creating the client:

```python
from HelpingAI import HAI

hai = HAI(api_key='your-api-key-here')
```

### Method 3: Configuration File

Create a `.env` file in your project root:

```env
HAI_API_KEY=your-api-key-here
```

Then load it in your Python code:

```python
import os
from dotenv import load_dotenv
from HelpingAI import HAI

load_dotenv()
hai = HAI()  # Will automatically use HAI_API_KEY from environment
```

## 🚀 Your First Request

Let's make your first API call:

```python
from HelpingAI import HAI

# Initialize the client
hai = HAI()

# Create a simple chat completion
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Hello! Can you help me understand emotional intelligence?"}
    ]
)

# Print the AI's response
print(response.choices[0].message.content)
```

## 🤖 Understanding Models

### Available Models

List all available models:

```python
# Get all available models
models = hai.models.list()
for model in models:
    print(f"Model ID: {model.id}")
    print(f"Model Name: {model.name}")
```

### Model Selection

We offer two powerful models:

**Dhanishtha-2.0-preview** - Revolutionary Reasoning Model:
- World's first intermediate thinking model with multi-phase reasoning
- Features transparent `<think>...</think>` blocks and self-correction
- Best for complex problem-solving and analytical tasks

**Dhanishtha-2.0-preview-mini** - Lightweight Reasoning Model:
- Efficient version of Dhanishtha-2.0-preview
- Same reasoning capabilities in a more compact model
- Best for faster responses and resource-constrained environments

```python
# Use Dhanishtha-2.0-preview for complex reasoning
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Solve this logic puzzle step by step"}],
    hide_think=False  # Show the thinking process
)

# Use Dhanishtha-2.0-preview-mini for faster responses
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview-mini",
    messages=[{"role": "user", "content": "Summarize the key points of emotional intelligence"}],
    hide_think=True  # Hide the thinking process for cleaner output
)
```

## 💬 Chat Completions

### Basic Chat

```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant with emotional intelligence."},
        {"role": "user", "content": "What are the key components of emotional intelligence?"}
    ]
)

print(response.choices[0].message.content)
```

### Multi-turn Conversations

Maintain conversation context by keeping message history:

```python
# Initialize conversation
conversation = [
    {"role": "system", "content": "You are HelpingAI, an emotionally intelligent assistant."},
    {"role": "user", "content": "What is empathy?"}
]

# First exchange
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=conversation
)

# Add AI response to conversation
conversation.append({
    "role": "assistant",
    "content": response.choices[0].message.content
})

# Continue the conversation
conversation.append({
    "role": "user",
    "content": "How can I develop better empathy skills?"
})

# Get next response
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=conversation
)
```

## 🌊 Streaming Responses

For real-time applications, use streaming to get responses as they're generated:

```python
# Basic streaming
response_stream = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Tell me a story about kindness"}],
    stream=True
)

# Print response as it streams
for chunk in response_stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Advanced Streaming with Error Handling

```python
def stream_with_error_handling(messages):
    try:
        response_stream = hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=messages,
            stream=True
        )
        
        full_response = ""
        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
                
        return full_response
        
    except Exception as e:
        print(f"Streaming error: {e}")
        return None

# Usage
result = stream_with_error_handling([
    {"role": "user", "content": "Explain the importance of emotional regulation"}
])
```

## ⚙️ Parameter Configuration

Fine-tune your AI responses with various parameters:

```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Write a creative story"}],
    
    # Creativity and randomness
    temperature=0.8,         # 0.0 = deterministic, 1.0 = very creative
    top_p=0.9,              # Nucleus sampling (0.1 = focused, 1.0 = diverse)
    
    # Response length
    max_tokens=500,         # Maximum tokens in response
    
    # Repetition control
    frequency_penalty=0.3,  # Reduce word repetition (-2.0 to 2.0)
    presence_penalty=0.3,   # Encourage topic diversity (-2.0 to 2.0)
    
    # Stop sequences
    stop=["END", "STOP"],   # Stop generation at these sequences
    
    # Special features
    hide_think=True,        # Filter out reasoning blocks
)
```

### Parameter Guidelines

| Parameter | Range | Description | Recommended |
|-----------|-------|-------------|-------------|
| `temperature` | 0.0-1.0 | Controls randomness | 0.7 for creative, 0.3 for factual |
| `top_p` | 0.0-1.0 | Nucleus sampling | 0.9 for most cases |
| `max_tokens` | 1-4096 | Response length limit | 500-1000 for conversations |
| `frequency_penalty` | -2.0-2.0 | Reduces repetition | 0.3 for variety |
| `presence_penalty` | -2.0-2.0 | Encourages new topics | 0.3 for diversity |

## 🛡️ Error Handling

Implement robust error handling for production applications:

```python
from HelpingAI import (
    HAI, HAIError, RateLimitError, InvalidRequestError, 
    AuthenticationError, ServiceUnavailableError
)
import time

def robust_completion(messages, max_retries=3):
    """Make a completion with comprehensive error handling."""
    
    for attempt in range(max_retries):
        try:
            return hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=messages
            )
            
        except RateLimitError as e:
            print(f"Rate limited. Waiting {e.retry_after or 60} seconds...")
            if attempt < max_retries - 1:
                time.sleep(e.retry_after or 60)
            else:
                raise
                
        except AuthenticationError as e:
            print(f"Authentication failed: {e}")
            raise  # Don't retry auth errors
            
        except InvalidRequestError as e:
            print(f"Invalid request: {e}")
            raise  # Don't retry invalid requests
            
        except ServiceUnavailableError as e:
            print(f"Service unavailable. Retrying in 30 seconds...")
            if attempt < max_retries - 1:
                time.sleep(30)
            else:
                raise
                
        except HAIError as e:
            print(f"API error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise

# Usage
try:
    response = robust_completion([
        {"role": "user", "content": "Hello!"}
    ])
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Failed after all retries: {e}")
```

## 🔧 Advanced Configuration

### Custom Client Configuration

```python
hai = HAI(
    api_key="your-api-key",
    base_url="https://api.helpingai.co/v1",  # Custom API endpoint
    timeout=30.0,                            # Request timeout in seconds
    organization="your-org-id"               # Organization ID (if applicable)
)
```

### Session Management

For applications making many requests, reuse the client instance:

```python
# Good: Reuse client
hai = HAI()

def process_multiple_requests(message_list):
    responses = []
    for messages in message_list:
        response = hai.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages
        )
        responses.append(response.choices[0].message.content)
    return responses

# Avoid: Creating new client for each request
def inefficient_processing(message_list):
    responses = []
    for messages in message_list:
        hai = HAI()  # Don't do this!
        response = hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=messages
        )
        responses.append(response.choices[0].message.content)
    return responses
```

## 📊 Response Analysis

Understanding the response structure:

```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Response metadata
print(f"Response ID: {response.id}")
print(f"Model used: {response.model}")
print(f"Created at: {response.created}")

# Message content
message = response.choices[0].message
print(f"Role: {message.role}")
print(f"Content: {message.content}")

# Token usage (if available)
if response.usage:
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")

# Finish reason
print(f"Finish reason: {response.choices[0].finish_reason}")
```

## 🎯 Best Practices

### 1. Security
- Always use environment variables for API keys
- Never commit API keys to version control
- Rotate API keys regularly

### 2. Performance
- Reuse client instances
- Implement appropriate timeouts
- Use streaming for long responses

### 3. Error Handling
- Implement retry logic for transient errors
- Handle rate limits gracefully
- Log errors for debugging

### 4. Cost Optimization
- Monitor token usage
- Use appropriate `max_tokens` limits
- Cache responses when possible

### 5. User Experience
- Use streaming for real-time feel
- Implement loading indicators
- Handle errors gracefully in UI

## 🚀 Next Steps

Now that you're set up, explore more advanced features:

1. **[API Reference](api_reference.md)** - Complete API documentation
2. **[Examples](examples.md)** - More code examples and use cases
3. **[FAQ](faq.md)** - Common questions and solutions

## 💡 Quick Tips

- Start with `temperature=0.7` for balanced creativity
- Use `hide_think=True` to filter internal reasoning
- Implement exponential backoff for rate limit handling
- Keep conversation history for context-aware responses
- Monitor your API usage in the dashboard

## 🔧 Tool Calling Framework

HelpingAI provides a powerful tool calling framework that makes it easy to create AI-callable functions:

```python
from HelpingAI import HAI
from HelpingAI.tools import tools, get_tools, get_registry

# Define a tool using the @tools decorator
@tools
def calculate_mortgage(principal: float, interest_rate: float, years: int) -> dict:
    """Calculate monthly mortgage payment and total cost.
    
    Args:
        principal: Loan amount in dollars
        interest_rate: Annual interest rate (percentage)
        years: Loan term in years
    """
    monthly_rate = interest_rate / 100 / 12
    num_payments = years * 12
    
    # Calculate monthly payment
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    total_cost = monthly_payment * num_payments
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_cost": round(total_cost, 2),
        "total_interest": round(total_cost - principal, 2)
    }

# Use the tool with chat completions
hai = HAI()
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Calculate mortgage payment for $300,000 at 4.5% for 30 years"}],
    tools=get_tools(),  # Include all registered tools
    tool_choice="auto"  # Let the model decide when to use tools
)

# Handle tool calls in the response
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    # Execute the tool
    tool = get_registry().get_tool(function_name)
    result = tool.call(function_args)
    
    # Continue the conversation with the tool result
    follow_up = hai.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "user", "content": "Calculate mortgage payment for $300,000 at 4.5% for 30 years"},
            response.choices[0].message,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result)
            }
        ]
    )
    
    print(follow_up.choices[0].message.content)
```

### Advanced Tool Features

The `@tools` decorator automatically:
- Generates JSON schema from Python type hints
- Extracts parameter descriptions from docstrings
- Registers tools in a thread-safe global registry
- Validates parameters against the schema
- Provides comprehensive error handling

For more details on tool calling, see the [API Reference](api_reference.md) and [Examples](examples.md).

## 🆘 Getting Help

If you encounter issues:

1. Check the [FAQ](faq.md) for common solutions
2. Review the [API Reference](api_reference.md) for detailed documentation
3. Submit issues on [GitHub](https://github.com/HelpingAI/HelpingAI-python/issues)
4. Contact support at helpingaiemotional@gmail.com

---

**Ready to build with emotional intelligence? Let's get started! 🚀**