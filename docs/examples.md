# Examples

This page provides a variety of examples to help you get started with the HelpingAI Python SDK.

## Basic Chat Completion

This section demonstrates how to make basic, non-streaming chat completion requests to the HelpingAI API. These examples are suitable for single-turn interactions where you want the complete response at once.

### Simple Question and Answer

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

### Multi-turn Conversation

```python
from HelpingAI import HAI

client = HAI()

# Example: Building a conversation history
print("--- Multi-turn Conversation Example ---")

# Start with system message and initial user query
conversation = [
    {"role": "system", "content": "You are a knowledgeable programming tutor who explains concepts clearly and provides practical examples."},
    {"role": "user", "content": "Can you explain what Python decorators are?"}
]

# First response
response1 = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=conversation
)

print("Assistant:", response1.choices[0].message.content)

# Add the assistant's response to conversation history
conversation.append({
    "role": "assistant",
    "content": response1.choices[0].message.content
})

# Continue the conversation with a follow-up question
conversation.append({
    "role": "user",
    "content": "Can you show me a practical example of a decorator that measures execution time?"
})

# Second response with context
response2 = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=conversation
)

print("\nFollow-up response:")
print("Assistant:", response2.choices[0].message.content)
```

### Different System Prompts for Various Use Cases

```python
from HelpingAI import HAI

client = HAI()

# Example 1: Creative Writing Assistant
print("--- Creative Writing Assistant ---")
creative_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {
            "role": "system",
            "content": "You are a creative writing assistant. Help users craft engaging stories, develop characters, and improve their writing style. Be imaginative and supportive."
        },
        {
            "role": "user",
            "content": "Help me create an opening paragraph for a mystery novel set in a small coastal town."
        }
    ]
)

print("Creative Writing Response:")
print(creative_response.choices[0].message.content)

# Example 2: Technical Consultant
print("\n--- Technical Consultant ---")
technical_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {
            "role": "system",
            "content": "You are a senior software architect and technical consultant. Provide detailed, practical advice on software design, architecture patterns, and best practices. Focus on scalability, maintainability, and performance."
        },
        {
            "role": "user",
            "content": "What's the best approach for designing a microservices architecture for an e-commerce platform?"
        }
    ]
)

print("Technical Consultant Response:")
print(technical_response.choices[0].message.content)

# Example 3: Data Analysis Helper
print("\n--- Data Analysis Helper ---")
analysis_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {
            "role": "system",
            "content": "You are a data analysis expert. Help users understand data concepts, choose appropriate statistical methods, and interpret results. Explain complex concepts in simple terms."
        },
        {
            "role": "user",
            "content": "I have sales data for the past 12 months. What statistical methods should I use to identify trends and forecast next quarter's sales?"
        }
    ]
)

print("Data Analysis Response:")
print(analysis_response.choices[0].message.content)
```

### Using Response Parameters

```python
from HelpingAI import HAI

client = HAI()

print("--- Response Parameter Examples ---")

# Example 1: Controlling creativity with temperature
print("Low temperature (more focused):")
focused_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Write a short poem about autumn"}
    ],
    temperature=0.2  # Lower temperature for more focused output
)
print(focused_response.choices[0].message.content)

print("\nHigh temperature (more creative):")
creative_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Write a short poem about autumn"}
    ],
    temperature=0.8  # Higher temperature for more creative output
)
print(creative_response.choices[0].message.content)

# Example 2: Limiting response length
print("\n--- Limited Response Length ---")
short_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Explain machine learning in simple terms"}
    ],
    max_tokens=100  # Limit to roughly 100 tokens
)
print("Short explanation:")
print(short_response.choices[0].message.content)

# Example 3: Using stop sequences
print("\n--- Using Stop Sequences ---")
structured_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "List the top 5 programming languages and briefly explain each. Format as: 1. Language: Explanation"}
    ],
    stop=["6."]  # Stop before listing a 6th item
)
print("Structured list:")
print(structured_response.choices[0].message.content)
```

### Working with Response Objects

```python
from HelpingAI import HAI

client = HAI()

print("--- Working with Response Objects ---")

response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Explain the benefits of renewable energy"}
    ]
)

# Access response using both attribute and dictionary-style access
message = response.choices[0].message

print("Response Details:")
print(f"Model used: {response.model}")
print(f"Response ID: {response.id}")
print(f"Created at: {response.created}")

print(f"\nMessage details:")
print(f"Role: {message.role}")
print(f"Content length: {len(message.content)} characters")
print(f"Has tool calls: {bool(message.tool_calls)}")

# Dictionary-style access
print(f"\nDictionary-style access:")
print(f"Role: {message['role']}")
print(f"Content preview: {message['content'][:100]}...")

# Check finish reason
choice = response.choices[0]
print(f"\nFinish reason: {choice.finish_reason}")

# Token usage details
if response.usage:
    usage = response.usage
    print(f"\nDetailed token usage:")
    print(f"  Input tokens: {usage.prompt_tokens}")
    print(f"  Output tokens: {usage.completion_tokens}")
    print(f"  Total tokens: {usage.total_tokens}")
    
    # Calculate cost estimate (example rates)
    input_cost = usage.prompt_tokens * 0.0001  # Example rate
    output_cost = usage.completion_tokens * 0.0002  # Example rate
    total_cost = input_cost + output_cost
    print(f"  Estimated cost: ${total_cost:.6f}")
```

## Streaming Completions

Streaming allows you to receive and process the model's response incrementally, token by token, as it is generated. This is particularly useful for real-time applications like chatbots, live content generation, and interactive interfaces where immediate feedback is important.

To enable streaming, set the `stream` parameter to `True` in the `client.chat.completions.create()` method. The method will then return an iterator that yields `ChatCompletionChunk` objects.

### Basic Streaming Example

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

### Real-time Chatbot Interface

```python
from HelpingAI import HAI
import time

class StreamingChatbot:
    def __init__(self):
        self.client = HAI()
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant. Provide clear, concise responses."}
        ]
    
    def stream_response(self, user_input):
        """Stream a response to user input with real-time display"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        print(f"\n🤖 Assistant: ", end="", flush=True)
        
        # Create streaming response
        stream = self.client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=self.conversation_history,
            stream=True,
            temperature=0.7
        )
        
        # Collect the full response while streaming
        full_response = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
                
                # Add a small delay to simulate typing effect
                time.sleep(0.02)
            
            if chunk.choices[0].finish_reason:
                print()  # New line when complete
                break
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": full_response})
        
        return full_response

# Example usage
chatbot = StreamingChatbot()

print("=== Streaming Chatbot Demo ===")
print("Type 'quit' to exit")

# Simulate a conversation
demo_inputs = [
    "Hello! Can you explain what machine learning is?",
    "What are some practical applications of machine learning?",
    "How do I get started learning machine learning?"
]

for user_input in demo_inputs:
    print(f"\n👤 User: {user_input}")
    chatbot.stream_response(user_input)
    time.sleep(1)  # Brief pause between exchanges

print("\n--- Demo complete ---")
```

### Streaming with Progress Tracking

```python
from HelpingAI import HAI
import time

client = HAI()

def stream_with_progress(messages, show_progress=True):
    """Stream response with progress indicators and statistics"""
    
    print("🔄 Generating response...")
    
    stream = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages,
        stream=True
    )
    
    # Track streaming metrics
    start_time = time.time()
    token_count = 0
    chunks_received = 0
    full_response = ""
    
    print("\n📝 Response:")
    print("-" * 50)
    
    for chunk in stream:
        chunks_received += 1
        
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            token_count += len(content.split())  # Rough token estimate
            
            # Display content
            print(content, end="", flush=True)
            
            # Show progress every 10 chunks
            if show_progress and chunks_received % 10 == 0:
                elapsed = time.time() - start_time
                print(f"\n[📊 Progress: {token_count} tokens, {elapsed:.1f}s]", end="", flush=True)
        
        if chunk.choices[0].finish_reason:
            break
    
    # Final statistics
    total_time = time.time() - start_time
    tokens_per_second = token_count / total_time if total_time > 0 else 0
    
    print(f"\n\n" + "="*50)
    print(f"✅ Streaming Complete!")
    print(f"📈 Statistics:")
    print(f"   • Total chunks: {chunks_received}")
    print(f"   • Estimated tokens: {token_count}")
    print(f"   • Time taken: {total_time:.2f} seconds")
    print(f"   • Speed: {tokens_per_second:.1f} tokens/second")
    print(f"   • Response length: {len(full_response)} characters")
    
    return full_response

# Example usage
print("=== Streaming with Progress Tracking ===")

messages = [
    {"role": "user", "content": "Write a comprehensive guide on setting up a Python development environment, including virtual environments, package management, and IDE setup."}
]

response = stream_with_progress(messages)
```

### Streaming for Live Content Generation

```python
from HelpingAI import HAI
import time
import threading

class LiveContentGenerator:
    def __init__(self):
        self.client = HAI()
        self.is_streaming = False
        
    def generate_live_content(self, topic, content_type="article"):
        """Generate content live with real-time updates"""
        
        prompt = f"""
        Write a {content_type} about {topic}.
        Make it engaging, informative, and well-structured.
        Include practical examples and actionable insights.
        """
        
        messages = [
            {"role": "system", "content": f"You are an expert content writer specializing in creating high-quality {content_type}s."},
            {"role": "user", "content": prompt}
        ]
        
        print(f"🚀 Generating live {content_type} about: {topic}")
        print("=" * 60)
        
        self.is_streaming = True
        word_count = 0
        paragraph_count = 0
        
        # Start progress indicator in separate thread
        progress_thread = threading.Thread(target=self._show_live_stats, args=(lambda: word_count,))
        progress_thread.daemon = True
        progress_thread.start()
        
        stream = self.client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=messages,
            stream=True,
            temperature=0.7
        )
        
        content_buffer = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                content_buffer += content
                
                # Update word count
                word_count = len(content_buffer.split())
                
                # Count paragraphs
                paragraph_count = content_buffer.count('\n\n') + 1
                
                # Display content with typing effect
                print(content, end="", flush=True)
                time.sleep(0.01)  # Slight delay for readability
            
            if chunk.choices[0].finish_reason:
                break
        
        self.is_streaming = False
        
        print(f"\n\n{'='*60}")
        print(f"✅ Content generation complete!")
        print(f"📊 Final stats: {word_count} words, {paragraph_count} paragraphs")
        
        return content_buffer
    
    def _show_live_stats(self, word_count_func):
        """Show live statistics while streaming"""
        while self.is_streaming:
            time.sleep(2)
            if self.is_streaming:
                print(f"\r💭 Words generated: {word_count_func()}", end="", flush=True)
                print("\r" + " " * 30 + "\r", end="", flush=True)  # Clear line

# Example usage
generator = LiveContentGenerator()

print("=== Live Content Generation Demo ===")

# Generate different types of content
topics = [
    ("Python Best Practices", "guide"),
    ("Future of AI", "blog post"),
    ("Data Science Workflow", "tutorial")
]

for topic, content_type in topics[:1]:  # Just show one example
    content = generator.generate_live_content(topic, content_type)
    print(f"\n🎯 Generated {len(content)} characters of content")
    time.sleep(1)
```

### Streaming with Error Handling

```python
from HelpingAI import HAI, HAIError
import time

def robust_streaming(messages, max_retries=3):
    """Streaming with comprehensive error handling and retry logic"""
    
    client = HAI()
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}")
            
            stream = client.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=messages,
                stream=True,
                timeout=30  # Set timeout for streaming
            )
            
            response_content = ""
            chunk_count = 0
            
            for chunk in stream:
                chunk_count += 1
                
                try:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        response_content += content
                        print(content, end="", flush=True)
                    
                    if chunk.choices[0].finish_reason:
                        print(f"\n✅ Stream completed successfully!")
                        print(f"📊 Received {chunk_count} chunks")
                        return response_content
                        
                except (IndexError, AttributeError) as e:
                    print(f"\n⚠️ Chunk processing error: {e}")
                    continue
                    
        except HAIError as e:
            print(f"\n❌ API Error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print("❌ Max retries exceeded")
                raise
                
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            if attempt < max_retries - 1:
                print("⏳ Retrying...")
                time.sleep(1)
            else:
                raise
    
    return None

# Example usage
print("=== Robust Streaming Example ===")

messages = [
    {"role": "user", "content": "Explain the concept of blockchain technology and its applications in simple terms."}
]

try:
    result = robust_streaming(messages)
    if result:
        print(f"\n🎯 Successfully generated {len(result)} characters")
except Exception as e:
    print(f"\n💥 Final error: {e}")
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

To enable the model to use your defined tools, pass them to the `tools` parameter of `client.chat.completions.create()`. The `tool_choice` parameter controls how the model uses tools. The enhanced workflow provides automatic tool caching and helper methods for streamlined tool execution.

#### Traditional Tool Calling Approach

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
```

#### Enhanced Workflow with Helper Methods

The SDK provides helper methods that simplify tool execution and conversation management:

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools

client = HAI()

print("--- Enhanced Tool Workflow ---")

# Example: Streamlined tool execution with helper methods
messages = [{"role": "user", "content": "What's the weather in London and the stock price of GOOG?"}]

# Step 1: Create chat completion with tools (automatic caching)
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=get_tools(),  # Tools are automatically cached
    tool_choice="auto"
)

assistant_message = response.choices[0].message

if assistant_message.tool_calls:
    print("🔧 Model wants to use tools. Using helper methods for execution...")
    
    # Step 2: Execute all tool calls using helper method
    execution_results = client.chat.completions.execute_tool_calls(assistant_message)
    
    print("Tool execution results:")
    for result in execution_results:
        print(f"  - Tool: {result.get('tool_call_id', 'unknown')}")
        if 'error' in result:
            print(f"    Error: {result['error']}")
        else:
            print(f"    Success: {str(result['result'])[:100]}...")
    
    # Step 3: Create tool response messages using helper method
    tool_responses = client.chat.completions.create_tool_response_messages(execution_results)
    
    # Step 4: Continue conversation with results
    final_messages = messages + [assistant_message.to_dict()] + tool_responses
    
    final_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=final_messages
        # Note: No need to specify tools again - they're cached from the first call
    )
    
    print("\n✅ Final response:")
    print(final_response.choices[0].message.content)
else:
    print("No tools needed for this request")
    print(assistant_message.content)
```

#### Enhanced Caching Workflow

Demonstrate the automatic tool caching feature:

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools

client = HAI()

print("--- Enhanced Caching Workflow ---")

# Step 1: Use tools in chat completion (they get automatically cached)
print("Step 1: Initial tool usage with automatic caching")
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=get_tools()  # Tools are cached automatically
)

print("Initial response:", response.choices[0].message.content)

# Step 2: Now tools are cached - can call directly without configuration
print("\nStep 2: Direct tool calls using cached tools")

# Call tools directly without reconfiguration
weather_result = client.call("get_current_weather", {
    "location": "Tokyo",
    "unit": "celsius"
})

print(f"Direct weather call result: {weather_result}")

stock_result = client.call("get_stock_price", {
    "symbol": "AAPL"
})

print(f"Direct stock call result: {stock_result}")

# Step 3: Continue with more chat completions - tools still cached
print("\nStep 3: Additional chat completions with cached tools")
follow_up_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "What's the weather in Paris?"},
        response.choices[0].message,
        {"role": "user", "content": "Now compare that with the weather in Tokyo and AAPL stock price"}
    ]
    # No need to specify tools - they're still cached!
)

print("Follow-up response:", follow_up_response.choices[0].message.content)
```

#### Multiple Tool Calls and Forcing Specific Tools

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools

client = HAI()

print("--- Multiple Tool Calls and Forced Execution ---")

# Example 1: Multiple tool calls in one request
print("Example 1: Multiple tool calls")
multi_tool_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Get the weather in London and stock prices for both GOOG and AAPL"}],
    tools=get_tools(),
    tool_choice="auto"
)

if multi_tool_response.choices[0].message.tool_calls:
    print(f"Model wants to make {len(multi_tool_response.choices[0].message.tool_calls)} tool calls")
    
    # Execute all tools at once using helper method
    results = client.chat.completions.execute_tool_calls(multi_tool_response.choices[0].message)
    
    for i, result in enumerate(results, 1):
        print(f"Tool {i} result: {result['result']}")

# Example 2: Forcing a specific tool
print("\nExample 2: Forcing a specific tool")
forced_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Tell me about London"}],
    tools=get_tools(),
    tool_choice={"type": "function", "function": {"name": "get_current_weather"}}
)

print("Forced tool call response:")
if forced_response.choices[0].message.tool_calls:
    # Use the automatic execution
    results = client.chat.completions.execute_tool_calls(forced_response.choices[0].message)
    print(f"Forced weather result: {results[0]['result']}")
```

#### Working with Built-in Tools

```python
from HelpingAI import HAI

client = HAI()

print("--- Working with Built-in Tools ---")

# Example: Combining custom tools with built-in tools
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{
        "role": "user",
        "content": "Search for information about the current weather APIs and then create a Python script to demonstrate how to use them"
    }],
    tools=get_tools() + ["web_search", "code_interpreter"]  # Mix custom and built-in tools
)

print("Model response with mixed tools:")
print(response.choices[0].message.content)

# Tools are now cached - can use any of them directly
if response.choices[0].message.tool_calls:
    print("\nExecuting tool calls...")
    results = client.chat.completions.execute_tool_calls(response.choices[0].message)
    
    for result in results:
        print(f"Tool executed: {result.get('tool_call_id', 'unknown')}")

# Direct calls to built-in tools (now cached)
print("\nDirect calls to cached built-in tools:")

search_result = client.call("web_search", {
    "query": "weather API comparison 2024",
    "max_results": 3
})

print(f"Search completed: {len(str(search_result))} characters of results")

code_result = client.call("code_interpreter", {
    "code": """
print("Demonstrating cached tool usage:")
import datetime
print(f"Current time: {datetime.datetime.now()}")
print("Built-in tools are now cached and ready for use!")
"""
})

print(f"Code execution result: {code_result}")
```

#### Advanced Tool Configuration

```python
from HelpingAI import HAI

client = HAI()

print("--- Advanced Tool Configuration ---")

# Example 1: Using hide_think parameter with tools
print("Example 1: Clean output with hide_think")
clean_response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Get the weather in Paris and explain it clearly"}],
    tools=["web_search", "code_interpreter"],
    hide_think=True  # Filter out internal reasoning for cleaner output
)

print("Clean response:")
print(clean_response.choices[0].message.content)

# Example 2: Streaming with tools
print("\nExample 2: Streaming tool responses")
stream = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Tell me a story about data analysis"}],
    tools=["code_interpreter"],
    stream=True,
    hide_think=True
)

print("Streaming response:")
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.choices[0].finish_reason:
        print(f"\n\nStream finished: {chunk.choices[0].finish_reason}")
        break

print("\nStreaming complete.")
```

## Built-in Tools

The HelpingAI SDK includes powerful built-in tools that provide essential functionality for AI applications. This section demonstrates how to use the built-in `code_interpreter` and `web_search` tools in various scenarios.

### Code Interpreter Examples

The `code_interpreter` tool provides Python code execution in a secure sandboxed environment with comprehensive data science capabilities. It automatically includes popular libraries like numpy, pandas, matplotlib, and seaborn.

#### Data Analysis with Pandas

```python
from HelpingAI import HAI

client = HAI()

# Example: Analyzing sales data
messages = [
    {"role": "user", "content": """
    I have sales data with the following records:
    - January: $12,500
    - February: $15,800  
    - March: $11,200
    - April: $18,900
    - May: $16,400
    
    Please create a pandas DataFrame with this data, calculate basic statistics, 
    and show the month with highest sales.
    """}
]

print("--- Data Analysis Example ---")
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=["code_interpreter"]  # Enable code interpreter
)

# The model will automatically use code_interpreter to analyze the data
print("Model's response:")
print(response.choices[0].message.content)

# If the model made tool calls, we can see the executed code
if response.choices[0].message.tool_calls:
    print("\nCode executed by the model:")
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "code_interpreter":
            import json
            args = json.loads(tool_call.function.arguments)
            print(args["code"])
```

#### Plot Generation and Visualization

```python
from HelpingAI import HAI

client = HAI()

# Example: Creating visualizations
messages = [
    {"role": "user", "content": """
    Create a matplotlib visualization showing the following quarterly revenue data:
    Q1: $125,000, Q2: $158,000, Q3: $142,000, Q4: $189,000
    
    Please create both a bar chart and a line plot, add proper labels and titles,
    and save the plots as files.
    """}
]

print("--- Visualization Example ---")
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=["code_interpreter"]
)

print("Model's response:")
print(response.choices[0].message.content)
```

#### Mathematical Computations

```python
from HelpingAI import HAI

client = HAI()

# Example: Complex mathematical calculations
messages = [
    {"role": "user", "content": """
    Calculate the following using numpy:
    1. Generate 1000 random numbers from a normal distribution (mean=50, std=15)
    2. Calculate mean, median, standard deviation, and 95th percentile
    3. Create a histogram of the distribution
    4. Perform a statistical test to check if the sample follows normal distribution
    """}
]

print("--- Mathematical Computation Example ---")
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=["code_interpreter"]
)

print("Model's response:")
print(response.choices[0].message.content)
```

#### Direct Code Interpreter Usage

You can also call the code interpreter directly using `client.call()`:

```python
from HelpingAI import HAI

client = HAI()

# Configure code interpreter
client.configure_tools(["code_interpreter"])

# Direct code execution
print("--- Direct Code Execution ---")
result = client.call("code_interpreter", {
    "code": """
import pandas as pd
import numpy as np

# Create sample data
data = {
    'Product': ['A', 'B', 'C', 'D', 'E'],
    'Sales': [1200, 1800, 1500, 2100, 1650],
    'Profit_Margin': [0.15, 0.22, 0.18, 0.25, 0.20]
}

df = pd.DataFrame(data)
print("Sales Data:")
print(df)

# Calculate total revenue and average profit margin
total_sales = df['Sales'].sum()
avg_margin = df['Profit_Margin'].mean()

print(f"\\nTotal Sales: ${total_sales:,}")
print(f"Average Profit Margin: {avg_margin:.2%}")

# Find best performing product
best_product = df.loc[df['Sales'].idxmax()]
print(f"\\nBest Performing Product:")
print(f"Product {best_product['Product']}: ${best_product['Sales']} sales, {best_product['Profit_Margin']:.1%} margin")
"""
})

print("Execution result:")
print(result)
```

## Comprehensive Error Handling

This section demonstrates how to handle various types of errors that may occur when using the HelpingAI SDK.

### Basic Error Handling

```python
from HelpingAI import HAI, HAIError, AuthenticationError, InvalidRequestError

client = HAI()

print("--- Basic Error Handling ---")

# Example 1: Invalid model error
try:
    response = client.chat.completions.create(
        model="non-existent-model",
        messages=[{"role": "user", "content": "Hello"}]
    )
except HAIError as e:
    print(f"API Error occurred: {e}")
    print(f"Error type: {type(e).__name__}")

# Example 2: Authentication error (with invalid API key)
try:
    invalid_client = HAI(api_key="invalid-key-12345")
    response = invalid_client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "Hello"}]
    )
except AuthenticationError as e:
    print(f"\nAuthentication Error: {e}")
except HAIError as e:
    print(f"\nGeneral API Error: {e}")

# Example 3: Invalid request error
try:
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "invalid-role", "content": "Hello"}]  # Invalid role
    )
except InvalidRequestError as e:
    print(f"\nInvalid Request Error: {e}")
except HAIError as e:
    print(f"\nGeneral API Error: {e}")
```

### Tool-Specific Error Handling

```python
from HelpingAI import HAI
from HelpingAI.tools.errors import ToolExecutionError, SchemaValidationError

client = HAI()

print("--- Tool-Specific Error Handling ---")

# Example 1: Tool execution error
try:
    client.configure_tools(["code_interpreter"])
    
    # This will cause an execution error due to invalid Python code
    result = client.call("code_interpreter", {
        "code": "print('Hello' + 123 + undefined_variable)"  # Invalid code
    })
except ToolExecutionError as e:
    print(f"Tool Execution Error: {e}")
    print(f"Tool name: {getattr(e, 'tool_name', 'Unknown')}")
except Exception as e:
    print(f"Unexpected error: {e}")

# Example 2: Schema validation error
try:
    # Invalid arguments for web_search tool
    client.configure_tools(["web_search"])
    result = client.call("web_search", {
        "query": "",  # Empty query
        "max_results": 15  # Exceeds maximum of 10
    })
except SchemaValidationError as e:
    print(f"\nSchema Validation Error: {e}")
except Exception as e:
    print(f"\nUnexpected error: {e}")

# Example 3: Tool not found error
try:
    result = client.call("non_existent_tool", {"param": "value"})
except ValueError as e:
    print(f"\nTool Not Found Error: {e}")
```

### Comprehensive Error Handling with Retry Logic

```python
from HelpingAI import HAI, HAIError, RateLimitError, APIConnectionError
import time
import random

def robust_api_call(client, max_retries=3, base_delay=1):
    """
    Make an API call with comprehensive error handling and retry logic
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=[
                    {"role": "user", "content": "Explain the concept of machine learning"}
                ],
                tools=["web_search"]
            )
            return response
            
        except RateLimitError as e:
            print(f"Rate limit exceeded (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Waiting {delay:.2f} seconds before retry...")
                time.sleep(delay)
            else:
                print("Max retries exceeded for rate limit")
                raise
                
        except APIConnectionError as e:
            print(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (attempt + 1)
                print(f"Waiting {delay} seconds before retry...")
                time.sleep(delay)
            else:
                print("Max retries exceeded for connection error")
                raise
                
        except HAIError as e:
            print(f"API error that should not be retried: {e}")
            raise
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

# Example usage of robust API call
print("--- Robust API Call with Error Handling ---")

client = HAI()

try:
    response = robust_api_call(client)
    print("API call successful!")
    print(f"Response: {response.choices[0].message.content[:100]}...")
    
except Exception as e:
    print(f"Final error after all retries: {e}")
```

### Error Handling in Tool Workflows

```python
from HelpingAI import HAI
import json

def safe_tool_workflow(client, user_message):
    """
    Demonstrate safe tool workflow with comprehensive error handling
    """
    try:
        # Step 1: Initial chat completion
        response = client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[{"role": "user", "content": user_message}],
            tools=["web_search", "code_interpreter"]
        )
        
        assistant_message = response.choices[0].message
        
        if not assistant_message.tool_calls:
            return assistant_message.content
        
        # Step 2: Execute tool calls with error handling
        tool_results = []
        for tool_call in assistant_message.tool_calls:
            try:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Executing tool: {function_name}")
                result = client.call(function_name, function_args)
                
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result)
                })
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error for tool {function_name}: {e}")
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps({"error": f"Invalid arguments: {e}"})
                })
                
            except Exception as e:
                print(f"Tool execution error for {function_name}: {e}")
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps({"error": str(e)})
                })
        
        # Step 3: Continue conversation with tool results
        messages = [
            {"role": "user", "content": user_message},
            assistant_message.to_dict(),
            *tool_results
        ]
        
        final_response = client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=messages
        )
        
        return final_response.choices[0].message.content
        
    except Exception as e:
        return f"Workflow error: {e}"

# Example usage
print("--- Safe Tool Workflow ---")

client = HAI()

# Test with a request that involves both tools
result = safe_tool_workflow(
    client,
    "Search for Python data science trends and create a visualization of the findings"
)

print("Workflow result:")
print(result)
```
### Web Search Examples

The `web_search` tool provides real-time web search functionality, allowing you to access current information from the internet.

#### Real-time Information Retrieval

```python
from HelpingAI import HAI

client = HAI()

# Example: Getting current information
messages = [
    {"role": "user", "content": "What are the latest developments in artificial intelligence this week? Please search for recent AI news and summarize the key points."}
]

print("--- Real-time AI News Search ---")
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=["web_search"]  # Enable web search
)

print("Model's response with current information:")
print(response.choices[0].message.content)
```

#### Research Assistant Example

```python
from HelpingAI import HAI

client = HAI()

# Example: Research on a specific topic
messages = [
    {"role": "user", "content": """
    I'm researching sustainable energy solutions. Please search for:
    1. Latest solar panel efficiency breakthroughs
    2. Current wind energy technology advances
    3. Battery storage innovations
    
    Provide a comprehensive summary with sources.
    """}
]

print("--- Research Assistant Example ---")
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=["web_search"]
)

print("Research summary:")
print(response.choices[0].message.content)
```

#### Direct Web Search Usage

```python
from HelpingAI import HAI

client = HAI()

# Configure web search
client.configure_tools(["web_search"])

# Direct search execution
print("--- Direct Web Search ---")
search_results = client.call("web_search", {
    "query": "Python machine learning libraries 2024",
    "max_results": 5
})

print("Search results:")
print(search_results)

# Search for specific information
print("\n--- Targeted Search ---")
specific_results = client.call("web_search", {
    "query": "GPT-4 latest updates and features",
    "max_results": 3
})

print("Specific search results:")
print(specific_results)
```

#### Current Events and News

```python
from HelpingAI import HAI

client = HAI()

# Example: Getting current events
messages = [
    {"role": "user", "content": "What are the top technology news stories today? Please search and provide a brief summary of the most important developments."}
]

print("--- Current Tech News ---")
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=["web_search"]
)

print("Today's tech news summary:")
print(response.choices[0].message.content)
```

## Advanced Workflow Examples

The HelpingAI SDK features an enhanced tool workflow with automatic caching that makes tool usage more seamless and efficient.

### Enhanced Tool Caching Workflow

The enhanced workflow allows you to use tools in chat completions and then call them directly without reconfiguration:

```python
from HelpingAI import HAI

client = HAI()

print("--- Enhanced Tool Caching Workflow ---")

# Step 1: Use tools in chat completion (tools are automatically cached)
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Search for Python data science tutorials and then analyze the search results"}
    ],
    tools=["web_search", "code_interpreter"]  # These tools are now cached
)

print("Initial response:")
print(response.choices[0].message.content)

# Step 2: Tools are now automatically cached - can call directly without reconfiguration
print("\n--- Direct Tool Calls (using cached tools) ---")

# Call web search directly (no need to configure again)
search_results = client.call("web_search", {
    "query": "advanced Python data science techniques 2024",
    "max_results": 3
})

print("Additional search results:")
print(search_results)

# Call code interpreter directly (also cached from the previous chat completion)
analysis_result = client.call("code_interpreter", {
    "code": """
# Analyze the search workflow
import datetime

print("Tool Caching Workflow Analysis:")
print(f"Timestamp: {datetime.datetime.now()}")
print("Benefits of enhanced workflow:")
benefits = [
    "Automatic tool configuration caching",
    "Seamless transition between chat and direct calls", 
    "Reduced setup overhead",
    "Improved developer experience"
]

for i, benefit in enumerate(benefits, 1):
    print(f"{i}. {benefit}")
"""
})

print("\nWorkflow analysis:")
print(analysis_result)
```

### Helper Methods Examples

The SDK provides powerful helper methods that simplify working with tool calls and message creation.

#### Complete Tool Execution Workflow

```python
from HelpingAI import HAI
import json

client = HAI()

print("--- Complete Tool Execution Workflow ---")

# Step 1: Create chat completion with tools
messages = [
    {"role": "user", "content": "Search for the latest Python frameworks and create a comparison chart"}
]

response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=["web_search", "code_interpreter"]
)

# Step 2: Check if the model made tool calls
assistant_message = response.choices[0].message
print("Assistant wants to make tool calls:", bool(assistant_message.tool_calls))

if assistant_message.tool_calls:
    # Step 3: Execute the tool calls using helper method
    print("\n--- Executing Tool Calls ---")
    execution_results = client.chat.completions.execute_tool_calls(assistant_message)
    
    print("Tool execution results:")
    for result in execution_results:
        print(f"Tool Call ID: {result['tool_call_id']}")
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Result: {str(result['result'])[:200]}...")  # Truncate for display
    
    # Step 4: Create tool response messages using helper method
    tool_responses = client.chat.completions.create_tool_response_messages(execution_results)
    
    # Step 5: Continue the conversation with tool results
    conversation_messages = messages + [assistant_message.to_dict()] + tool_responses
    
    # Step 6: Get final response with tool results
    final_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=conversation_messages
    )
    
    print("\n--- Final Response After Tool Execution ---")
    print(final_response.choices[0].message.content)
```

#### Creating Assistant Messages with Helper Methods

```python
from HelpingAI import HAI

client = HAI()

print("--- Creating Assistant Messages ---")

# Create an assistant message with content
assistant_msg_1 = client.chat.completions.create_assistant_message(
    content="I'll help you analyze the data. Let me search for relevant information first."
)

print("Assistant message with content:")
print(f"Role: {assistant_msg_1.role}")
print(f"Content: {assistant_msg_1.content}")

# Create an assistant message with tool calls
from HelpingAI.models import ToolCall, ToolFunction

tool_call = ToolCall(
    id="call_123",
    type="function",
    function=ToolFunction(
        name="web_search",
        arguments='{"query": "machine learning best practices", "max_results": 5}'
    )
)

assistant_msg_2 = client.chat.completions.create_assistant_message(
    content="I'll search for machine learning best practices.",
    tool_calls=[tool_call]
)

print("\nAssistant message with tool calls:")
print(f"Role: {assistant_msg_2.role}")
print(f"Content: {assistant_msg_2.content}")
print(f"Tool calls: {len(assistant_msg_2.tool_calls)}")
```

## Practical Use Case Examples

This section demonstrates complete, real-world scenarios that combine multiple features of the HelpingAI SDK.

### Data Analysis Assistant

A complete example showing how to build a data analysis assistant that can search for data, analyze it, and create visualizations:

```python
from HelpingAI import HAI

def data_analysis_assistant():
    """Complete data analysis assistant example"""
    client = HAI()
    
    print("=== Data Analysis Assistant ===")
    
    # Step 1: Get data analysis request
    user_request = """
    I need to analyze stock market performance. Please:
    1. Search for recent information about S&P 500 performance
    2. Create sample stock data for analysis
    3. Calculate key metrics and create visualizations
    4. Provide insights and recommendations
    """
    
    # Step 2: Initial analysis with web search
    print("Step 1: Gathering market information...")
    search_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": user_request}],
        tools=["web_search", "code_interpreter"]
    )
    
    print("Market research completed.")
    print(search_response.choices[0].message.content)
    
    # Step 3: Detailed data analysis
    print("\nStep 2: Performing detailed analysis...")
    analysis_request = """
    Now create a comprehensive analysis with the following:
    1. Generate sample portfolio data (10 stocks with prices, volumes, sectors)
    2. Calculate portfolio metrics (total value, sector allocation, risk metrics)
    3. Create visualizations (pie chart for sectors, line chart for performance)
    4. Generate a summary report with recommendations
    """
    
    analysis_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "user", "content": user_request},
            search_response.choices[0].message,
            {"role": "user", "content": analysis_request}
        ],
        tools=["code_interpreter"]
    )
    
    print("Analysis completed:")
    print(analysis_response.choices[0].message.content)
    
    return analysis_response

# Run the data analysis assistant
if __name__ == "__main__":
    result = data_analysis_assistant()
```

### Research Assistant

A comprehensive research assistant that combines web search with analysis and report generation:

```python
from HelpingAI import HAI

def research_assistant(topic):
    """Comprehensive research assistant example"""
    client = HAI()
    
    print(f"=== Research Assistant: {topic} ===")
    
    # Step 1: Comprehensive web search
    search_query = f"""
    I need to research {topic}. Please search for:
    1. Latest developments and trends
    2. Key players and companies
    3. Market size and growth projections
    4. Challenges and opportunities
    
    Gather comprehensive information from multiple sources.
    """
    
    print("Step 1: Gathering research data...")
    research_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": search_query}],
        tools=["web_search"]
    )
    
    # Step 2: Analysis and report generation
    analysis_query = """
    Based on the research data, please:
    1. Create a structured analysis with key findings
    2. Generate charts showing market trends or key metrics
    3. Identify top 5 key insights
    4. Create a summary table of important data points
    5. Provide strategic recommendations
    """
    
    print("Step 2: Analyzing research data...")
    analysis_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "user", "content": search_query},
            research_response.choices[0].message,
            {"role": "user", "content": analysis_query}
        ],
        tools=["code_interpreter"]
    )
    
    print("Research Analysis:")
    print(analysis_response.choices[0].message.content)
    
    return {
        "research_data": research_response.choices[0].message.content,
        "analysis": analysis_response.choices[0].message.content
    }

# Example usage
if __name__ == "__main__":
    result = research_assistant("artificial intelligence in healthcare")
    
    # Additional follow-up analysis
    client = HAI()
    client.configure_tools(["code_interpreter"])
    
    # Generate executive summary
    summary = client.call("code_interpreter", {
        "code": """
# Generate executive summary
research_topic = "AI in Healthcare"

print(f"EXECUTIVE SUMMARY: {research_topic}")
print("=" * 50)

key_points = [
    "Market Growth: AI healthcare market projected to reach $102B by 2028",
    "Key Applications: Diagnostics, drug discovery, personalized medicine",
    "Major Players: Google Health, IBM Watson, Microsoft Healthcare Bot",
    "Challenges: Data privacy, regulatory approval, integration costs",
    "Opportunities: Improved patient outcomes, cost reduction, efficiency gains"
]

for i, point in enumerate(key_points, 1):
    print(f"{i}. {point}")

print("\\nRECOMMENDATIONS:")
recommendations = [
    "Focus on regulatory-compliant solutions",
    "Invest in data security and privacy",
    "Partner with healthcare institutions for pilot programs",
    "Develop interoperable platforms"
]

for i, rec in enumerate(recommendations, 1):
    print(f"• {rec}")
"""
    })
    
    print("\n" + "="*60)
    print(summary)
```

### Interactive Chatbot with Tool Calling

A complete example of an interactive chatbot that can use multiple tools based on user requests:

```python
from HelpingAI import HAI

class InteractiveChatbot:
    def __init__(self):
        self.client = HAI()
        self.conversation_history = []
        
    def add_message(self, role, content):
        """Add a message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
    
    def chat(self, user_input):
        """Process user input and generate response"""
        self.add_message("user", user_input)
        
        # Create response with all available tools
        response = self.client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=self.conversation_history,
            tools=["web_search", "code_interpreter"],
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Handle tool calls if any
        if assistant_message.tool_calls:
            print("🔧 Using tools to help with your request...")
            
            # Execute tool calls
            execution_results = self.client.chat.completions.execute_tool_calls(assistant_message)
            
            # Create tool response messages
            tool_responses = self.client.chat.completions.create_tool_response_messages(execution_results)
            
            # Add assistant message and tool responses to history
            self.conversation_history.append(assistant_message.to_dict())
            self.conversation_history.extend(tool_responses)
            
            # Get final response after tool execution
            final_response = self.client.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=self.conversation_history,
                tools=["web_search", "code_interpreter"]
            )
            
            final_message = final_response.choices[0].message.content
            self.add_message("assistant", final_message)
            
            return final_message
        else:
            # No tools needed, just add the response
            self.add_message("assistant", assistant_message.content)
            return assistant_message.content
    
    def run_interactive_session(self):
        """Run an interactive chat session"""
        print("🤖 Interactive Chatbot with Tool Calling")
        print("Type 'quit' to exit, 'history' to see conversation history")
        print("-" * 50)
        
        while True:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'history':
                print("\n📜 Conversation History:")
                for i, msg in enumerate(self.conversation_history, 1):
                    print(f"{i}. {msg['role'].title()}: {msg['content'][:100]}...")
                continue
            elif not user_input:
                continue
            
            try:
                response = self.chat(user_input)
                print(f"\n🤖 Assistant: {response}")
            except Exception as e:
                print(f"\n❌ Error: {e}")

# Example usage
if __name__ == "__main__":
    # Create and run the chatbot
    bot = InteractiveChatbot()
    
    # Example automated conversation
    print("=== Example Conversation ===")
    
    responses = [
        "Hello! Can you help me with data analysis?",
        "Search for information about Python data visualization libraries",
        "Now create a sample chart comparing the popularity of matplotlib, seaborn, and plotly",
        "What are the current trends in machine learning?"
    ]
    
    for user_msg in responses:
        print(f"\n👤 User: {user_msg}")
        bot_response = bot.chat(user_msg)
        print(f"🤖 Bot: {bot_response}")
    
    # Uncomment to run interactive session
    # bot.run_interactive_session()
```

## BaseModel Dictionary-like Access Examples

All response objects in the HelpingAI SDK inherit from BaseModel, providing powerful dictionary-like access patterns alongside traditional attribute access.

### Dictionary-style Access Patterns

```python
from HelpingAI import HAI

client = HAI()

# Create a chat completion
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)

print("--- Dictionary-style Access Examples ---")

# Get the message object
message = response.choices[0].message

# Traditional attribute access
print("Traditional access:")
print(f"Role: {message.role}")
print(f"Content: {message.content}")

# Dictionary-style access
print("\nDictionary-style access:")
print(f"Role: {message['role']}")
print(f"Content: {message['content']}")

# Check if key exists
print(f"\nHas 'tool_calls' key: {'tool_calls' in message}")
print(f"Has 'role' key: {'role' in message}")

# Get with default value
content = message.get("content", "No content available")
tool_calls = message.get("tool_calls", [])
print(f"\nContent with default: {content[:50]}...")
print(f"Tool calls with default: {tool_calls}")

# Iterate like a dictionary
print("\nIterating over message fields:")
for key, value in message.items():
    if value is not None:
        value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        print(f"  {key}: {value_str}")

# Get all keys and values
print(f"\nAvailable keys: {list(message.keys())}")
print(f"Number of fields: {len(message)}")
```

### Working with Tool Calls using Dictionary Access

```python
from HelpingAI import HAI

client = HAI()

# Create a response that includes tool calls
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Search for Python tutorials and analyze the results"}],
    tools=["web_search", "code_interpreter"]
)

message = response.choices[0].message

print("--- Tool Calls Dictionary Access ---")

# Check for tool calls using dictionary access
if message.get("tool_calls"):
    print(f"Number of tool calls: {len(message['tool_calls'])}")
    
    for i, tool_call in enumerate(message["tool_calls"]):
        print(f"\nTool Call {i + 1}:")
        print(f"  ID: {tool_call['id']}")
        print(f"  Type: {tool_call['type']}")
        print(f"  Function Name: {tool_call['function']['name']}")
        
        # Access function arguments
        if 'arguments' in tool_call['function']:
            print(f"  Arguments: {tool_call['function']['arguments']}")
else:
    print("No tool calls in this response")

# Access response metadata using dictionary patterns
print("\n--- Response Metadata ---")
choice = response.choices[0]
print(f"Finish reason: {choice.get('finish_reason', 'Not specified')}")
print(f"Index: {choice.get('index', 'Not specified')}")

# Usage information
if 'usage' in response and response['usage']:
    usage = response['usage']
    print(f"\nToken usage:")
    print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
    print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
    print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")
```

### Converting Between Formats

```python
from HelpingAI import HAI

client = HAI()

response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

message = response.choices[0].message

print("--- Format Conversion Examples ---")

# Convert to dictionary (Pydantic-style)
message_dict = message.model_dump()
print("Pydantic model_dump():")
print(f"Type: {type(message_dict)}")
print(f"Keys: {list(message_dict.keys())}")

# Convert to JSON string (Pydantic-style)
message_json = message.model_dump_json()
print(f"\nPydantic model_dump_json() length: {len(message_json)} characters")

# Standard methods also available
message_dict_std = message.to_dict()
message_json_std = message.json()

print(f"\nStandard to_dict() keys: {list(message_dict_std.keys())}")
print(f"Standard json() length: {len(message_json_std)} characters")

# Create from dictionary (useful for conversation history)
new_message_data = {
    "role": "assistant",
    "content": "Hello! I'm doing well, thank you for asking."
}

# Using Pydantic-style validation
from HelpingAI.models import ChatCompletionMessage
new_message = ChatCompletionMessage.model_validate(new_message_data)

print(f"\nCreated message from dict:")
print(f"Role: {new_message['role']}")
print(f"Content: {new_message['content']}")

# Demonstrate mixed access patterns
print(f"\nMixed access patterns:")
print(f"Attribute access: {new_message.role}")
print(f"Dictionary access: {new_message['role']}")
print(f"Get method: {new_message.get('role', 'unknown')}")
```
