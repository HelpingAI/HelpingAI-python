# HelpingAI SDK Examples

Comprehensive examples demonstrating the capabilities of the HelpingAI Python SDK.

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Streaming](#streaming)
- [Error Handling](#error-handling)
- [Real-World Applications](#real-world-applications)
- [Best Practices](#best-practices)

## Installation & Setup

### Installation

```bash
pip install HelpingAI
```

### Environment Setup

```bash
# Set your API key
export HAI_API_KEY='your-api-key-here'
```

### Basic Client Initialization

```python
from HelpingAI import HAI
import os

# Method 1: Using environment variable
hai = HAI()

# Method 2: Direct API key
hai = HAI(api_key="your-api-key")

# Method 3: With custom configuration
hai = HAI(
    api_key=os.getenv("HAI_API_KEY"),
    timeout=30.0,
    base_url="https://api.helpingai.co/v1"
)
```

## Basic Usage

### Simple Chat Completion

```python
from HelpingAI import HAI

hai = HAI()

# Basic completion
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "user", "content": "Hello! Can you help me understand emotional intelligence?"}
    ]
)

print(response.choices[0].message.content)
```

### System Messages

```python
# Using system messages to set context
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "system", "content": "You are HelpingAI, an expert in emotional intelligence and psychology."},
        {"role": "user", "content": "What are the key components of emotional intelligence?"}
    ]
)

print(response.choices[0].message.content)
```

### Multi-turn Conversations

```python
# Maintain conversation context
conversation = [
    {"role": "system", "content": "You are a helpful AI assistant with emotional intelligence."},
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

# Continue conversation
conversation.append({
    "role": "user",
    "content": "How can I develop better empathy skills?"
})

response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=conversation
)

print(response.choices[0].message.content)
```

## Advanced Features

### Parameter Control

```python
# Fine-tuning response characteristics
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Write a creative story about friendship"}],
    
    # Creativity controls
    temperature=0.8,        # Higher = more creative (0.0-1.0)
    top_p=0.9,             # Nucleus sampling (0.0-1.0)
    
    # Length controls
    max_tokens=500,        # Maximum response length
    
    # Repetition controls
    frequency_penalty=0.3, # Reduce word repetition (-2.0 to 2.0)
    presence_penalty=0.3,  # Encourage topic diversity (-2.0 to 2.0)
    
    # Stop sequences
    stop=["THE END", "CONCLUSION"],
    
    # Special features
    hide_think=True,       # Filter out reasoning blocks
    seed=42               # For reproducible results
)

print(response.choices[0].message.content)
```

### Different Temperature Settings

```python
def compare_temperatures(prompt):
    """Compare responses at different temperature settings."""
    temperatures = [0.2, 0.7, 1.0]
    
    for temp in temperatures:
        print(f"\n--- Temperature: {temp} ---")
        response = hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=100
        )
        print(response.choices[0].message.content)

# Usage
compare_temperatures("Describe the color blue in one sentence.")
```

### Using Stop Sequences

```python
# Control where generation stops
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "List the benefits of meditation:"}],
    stop=["\n\n", "In conclusion", "Summary:"],
    max_tokens=200
)

print(response.choices[0].message.content)
```

## Streaming

### Basic Streaming

```python
# Stream responses in real-time
def stream_response(prompt):
    response_stream = hai.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    print("AI: ", end="", flush=True)
    for chunk in response_stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # New line at the end

# Usage
stream_response("Tell me about the importance of emotional regulation.")
```

### Advanced Streaming with Processing

```python
def stream_with_processing(prompt):
    """Stream with real-time processing and formatting."""
    response_stream = hai.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        hide_think=True
    )
    
    full_response = ""
    word_count = 0
    
    print("AI: ", end="", flush=True)
    for chunk in response_stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            
            # Track full response
            full_response += content
            
            # Count words
            word_count += len(content.split())
            
            # Add processing logic here
            # e.g., real-time sentiment analysis, keyword extraction, etc.
    
    print(f"\n\n[Response complete. Words: {word_count}]")
    return full_response

# Usage
result = stream_with_processing("Explain the concept of emotional contagion.")
```

### Streaming with Error Handling

```python
from HelpingAI import HAIError, RateLimitError, TimeoutError

def robust_streaming(prompt, max_retries=3):
    """Streaming with comprehensive error handling."""
    
    for attempt in range(max_retries):
        try:
            response_stream = hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                timeout=30.0
            )
            
            full_response = ""
            print("AI: ", end="", flush=True)
            
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print()  # New line
            return full_response
            
        except RateLimitError as e:
            print(f"\nRate limited. Waiting {e.retry_after or 60} seconds...")
            time.sleep(e.retry_after or 60)
            
        except TimeoutError:
            print(f"\nTimeout on attempt {attempt + 1}. Retrying...")
            
        except HAIError as e:
            print(f"\nAPI error: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None

# Usage
result = robust_streaming("Write a detailed explanation of mindfulness meditation.")
```

## Error Handling

### Comprehensive Error Handling

```python
from HelpingAI import (
    HAI, HAIError, RateLimitError, InvalidRequestError,
    AuthenticationError, ServiceUnavailableError, TimeoutError,
    InvalidModelError, ContentFilterError
)
import time
import random

def robust_completion(messages, max_retries=3):
    """Make a completion with comprehensive error handling."""
    
    for attempt in range(max_retries):
        try:
            return hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=messages
            )
            
        except RateLimitError as e:
            wait_time = e.retry_after or (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            
        except AuthenticationError as e:
            print(f"Authentication failed: {e}")
            print("Please check your API key.")
            raise  # Don't retry auth errors
            
        except InvalidModelError as e:
            print(f"Invalid model: {e}")
            print("Available models:")
            try:
                models = hai.models.list()
                for model in models:
                    print(f"  - {model.id}")
            except:
                print("  Could not fetch model list")
            raise  # Don't retry invalid model
            
        except InvalidRequestError as e:
            print(f"Invalid request: {e}")
            if hasattr(e, 'param'):
                print(f"Parameter issue: {e.param}")
            raise  # Don't retry invalid requests
            
        except ContentFilterError as e:
            print(f"Content filtered: {e}")
            print("Please modify your request to comply with content policy.")
            raise  # Don't retry filtered content
            
        except ServiceUnavailableError as e:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Service unavailable. Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            
        except TimeoutError as e:
            print(f"Request timed out on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            
        except HAIError as e:
            print(f"API error: {e}")
            if e.status_code and e.status_code >= 500:
                # Server error, retry with backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Server error. Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                raise  # Client error, don't retry
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    raise HAIError(f"Failed after {max_retries} attempts")

# Usage example
try:
    response = robust_completion([
        {"role": "user", "content": "Explain the benefits of emotional intelligence in leadership."}
    ])
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Final error: {e}")
```

### Context Manager for Error Handling

```python
from contextlib import contextmanager

@contextmanager
def hai_error_context():
    """Context manager for handling HAI API errors."""
    try:
        yield
    except RateLimitError as e:
        print(f"⚠️  Rate limited. Please wait {e.retry_after or 60} seconds.")
    except AuthenticationError as e:
        print(f"🔐 Authentication error: {e}")
    except InvalidRequestError as e:
        print(f"❌ Invalid request: {e}")
    except ServiceUnavailableError as e:
        print(f"🚫 Service unavailable. Please try again later.")
    except HAIError as e:
        print(f"🔥 API error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

# Usage
with hai_error_context():
    response = hai.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)
```

## Real-World Applications

### Chatbot Implementation

```python
class EmotionalChatbot:
    """A chatbot with emotional intelligence capabilities."""
    
    def __init__(self, api_key=None):
        self.hai = HAI(api_key=api_key)
        self.conversation_history = [
            {"role": "system", "content": """You are HelpingAI, an emotionally intelligent assistant. 
            You excel at understanding emotions, providing empathetic responses, and helping users 
            with emotional support and guidance. Always be kind, understanding, and supportive."""}
        ]
    
    def chat(self, user_message):
        """Process a user message and return a response."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Generate response
            response = self.hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=500,
                hide_think=True
            )
            
            ai_message = response.choices[0].message.content
            
            # Add AI response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message
            })
            
            return ai_message
            
        except Exception as e:
            return f"I'm sorry, I encountered an error: {e}"
    
    def stream_chat(self, user_message):
        """Stream a response to user message."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            response_stream = self.hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=self.conversation_history,
                stream=True,
                temperature=0.7,
                hide_think=True
            )
            
            full_response = ""
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
            
            return full_response
            
        except Exception as e:
            error_msg = f"I'm sorry, I encountered an error: {e}"
            print(error_msg)
            return error_msg
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = self.conversation_history[:1]  # Keep system message

# Usage
chatbot = EmotionalChatbot()

print("🤖 HelpingAI Chatbot (type 'quit' to exit)")
print("=" * 50)

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Goodbye! Take care! 👋")
        break
    
    print("AI: ", end="")
    chatbot.stream_chat(user_input)
```

### Content Analysis Tool

```python
class ContentAnalyzer:
    """Analyze content for emotional tone, sentiment, and insights."""
    
    def __init__(self, api_key=None):
        self.hai = HAI(api_key=api_key)
    
    def analyze_emotion(self, text):
        """Analyze the emotional content of text."""
        prompt = f"""
        Analyze the emotional content of the following text. Provide:
        1. Primary emotions detected
        2. Emotional intensity (1-10 scale)
        3. Overall sentiment (positive/negative/neutral)
        4. Key emotional indicators
        
        Text to analyze: "{text}"
        """
        
        response = self.hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[
                {"role": "system", "content": "You are an expert in emotional analysis and psychology."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            hide_think=True
        )
        
        return response.choices[0].message.content
    
    def suggest_improvements(self, text, context="general communication"):
        """Suggest improvements for emotional communication."""
        prompt = f"""
        Review the following text for emotional intelligence and communication effectiveness.
        Context: {context}
        
        Provide suggestions for:
        1. Improving emotional tone
        2. Enhancing empathy
        3. Better word choices
        4. Overall communication effectiveness
        
        Text: "{text}"
        """
        
        response = self.hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[
                {"role": "system", "content": "You are an expert communication coach specializing in emotional intelligence."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            hide_think=True
        )
        
        return response.choices[0].message.content

# Usage
analyzer = ContentAnalyzer()

# Analyze emotional content
text = "I'm really frustrated with this project. Nothing seems to be working right and I feel like giving up."
analysis = analyzer.analyze_emotion(text)
print("Emotional Analysis:")
print(analysis)

print("\n" + "="*50 + "\n")

# Get improvement suggestions
suggestions = analyzer.suggest_improvements(text, "workplace communication")
print("Improvement Suggestions:")
print(suggestions)
```

### Educational Assistant

```python
class EducationalAssistant:
    """An AI tutor focused on emotional intelligence education."""
    
    def __init__(self, api_key=None):
        self.hai = HAI(api_key=api_key)
        self.student_progress = {}
    
    def create_lesson(self, topic, difficulty_level="beginner"):
        """Create a personalized lesson on emotional intelligence topics."""
        prompt = f"""
        Create an engaging lesson on "{topic}" for a {difficulty_level} level student.
        
        Include:
        1. Clear explanation of the concept
        2. Real-world examples
        3. Practical exercises
        4. Reflection questions
        5. Key takeaways
        
        Make it interactive and engaging.
        """
        
        response = self.hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[
                {"role": "system", "content": "You are an expert educator specializing in emotional intelligence and psychology. Create engaging, practical lessons."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=800,
            hide_think=True
        )
        
        return response.choices[0].message.content
    
    def quiz_student(self, topic, num_questions=5):
        """Generate a quiz on the given topic."""
        prompt = f"""
        Create a {num_questions}-question quiz on "{topic}" related to emotional intelligence.
        
        Format each question as:
        Q1: [Question]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Correct Answer: [Letter]
        Explanation: [Brief explanation]
        
        Make questions practical and thought-provoking.
        """
        
        response = self.hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[
                {"role": "system", "content": "You are an educational assessment expert. Create meaningful quizzes that test understanding and application."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            hide_think=True
        )
        
        return response.choices[0].message.content
    
    def provide_feedback(self, student_response, correct_answer, topic):
        """Provide personalized feedback on student responses."""
        prompt = f"""
        A student answered a question about "{topic}".
        
        Student's response: "{student_response}"
        Correct answer: "{correct_answer}"
        
        Provide encouraging, constructive feedback that:
        1. Acknowledges what they got right
        2. Gently corrects misconceptions
        3. Provides additional insights
        4. Encourages continued learning
        """
        
        response = self.hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[
                {"role": "system", "content": "You are a supportive, encouraging tutor who provides constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            hide_think=True
        )
        
        return response.choices[0].message.content

# Usage
tutor = EducationalAssistant()

# Create a lesson
lesson = tutor.create_lesson("Active Listening", "intermediate")
print("📚 Lesson: Active Listening")
print("=" * 50)
print(lesson)

print("\n" + "="*50 + "\n")

# Generate a quiz
quiz = tutor.quiz_student("Active Listening", 3)
print("📝 Quiz: Active Listening")
print("=" * 50)
print(quiz)
```

## Best Practices

### Efficient API Usage

```python
class EfficientHAIClient:
    """Demonstrates efficient API usage patterns."""
    
    def __init__(self, api_key=None):
        # Reuse client instance
        self.hai = HAI(api_key=api_key)
        self.response_cache = {}
    
    def cached_completion(self, messages, cache_key=None):
        """Use caching for repeated requests."""
        if cache_key and cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        response = self.hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=messages,
            temperature=0.3  # Lower temperature for more consistent results
        )
        
        if cache_key:
            self.response_cache[cache_key] = response
        
        return response
    
    def batch_process(self, message_lists, delay=1.0):
        """Process multiple requests with rate limiting."""
        results = []
        
        for i, messages in enumerate(message_lists):
            try:
                response = self.hai.chat.completions.create(
                    model="Dhanishtha-2.0-preview",
                    messages=messages
                )
                results.append(response.choices[0].message.content)
                
                # Add delay to respect rate limits
                if i < len(message_lists) - 1:
                    time.sleep(delay)
                    
            except RateLimitError as e:
                print(f"Rate limited at request {i+1}. Waiting...")
                time.sleep(e.retry_after or 60)
                # Retry the same request
                response = self.hai.chat.completions.create(
                    model="Dhanishtha-2.0-preview",
                    messages=messages
                )
                results.append(response.choices[0].message.content)
        
        return results
    
    def optimize_tokens(self, messages, max_tokens=500):
        """Optimize token usage for cost efficiency."""
        # Estimate token count (rough approximation)
        total_chars = sum(len(msg["content"]) for msg in messages)
        estimated_tokens = total_chars // 4  # Rough estimate
        
        if estimated_tokens > 3000:  # Leave room for response
            print("⚠️  Input may be too long. Consider summarizing.")
        
        return self.hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )

# Usage
client = EfficientHAIClient()

# Cached requests
response1 = client.cached_completion(
    [{"role": "user", "content": "What is empathy?"}],
    cache_key="empathy_definition"
)

# This will use cached result
response2 = client.cached_completion(
    [{"role": "user", "content": "What is empathy?"}],
    cache_key="empathy_definition"
)
```

### Production-Ready Implementation

```python
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionHAIClient:
    """Production-ready HAI client with logging, monitoring, and error handling."""
    
    def __init__(self, api_key=None, log_requests=True):
        self.hai = HAI(api_key=api_key)
        self.log_requests = log_requests
        self.request_count = 0
        self.error_count = 0
    
    def _log_request(self, messages: list, response: Optional[Any] = None, error: Optional[Exception] = None):
        """Log request details for monitoring."""
        if not self.log_requests:
            return
        
        self.request_count += 1
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "request_id": self.request_count,
            "message_count": len(messages),
            "model": "Dhanishtha-2.0-preview"
        }
        
        if response:
            log_data.update({
                "success": True,
                "response_id": getattr(response, 'id', None),
                "tokens_used": getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') and response.usage else None
            })
            logger.info(f"Request successful: {json.dumps(log_data)}")
        
        if error:
            self.error_count += 1
            log_data.update({
                "success": False,
                "error_type": type(error).__name__,
                "error_message": str(error)
            })
            logger.error(f"Request failed: {json.dumps(log_data)}")
    
    def create_completion(self, messages: list, **kwargs) -> Optional[Any]:
        """Create completion with full production features."""
        try:
            response = self.hai.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=messages,
                **kwargs
            )
            
            self._log_request(messages, response=response)
            return response
            
        except Exception as e:
            self._log_request(messages, error=e)
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client usage statistics."""
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1) * 100,
            "error_rate": self.error_count / max(self.request_count, 1) * 100
        }

# Usage
client = ProductionHAIClient()

try:
    response = client.create_completion(
        messages=[{"role": "user", "content": "Hello!"}],
        temperature=0.7,
        max_tokens=200
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")

# Check statistics
stats = client.get_stats()
print(f"Success rate: {stats['success_rate']:.1f}%")
```

### Async Pattern (Conceptual)

```python
import asyncio
import concurrent.futures
from typing import List

class AsyncHAIWrapper:
    """Wrapper for async-like behavior using thread pools."""
    
    def __init__(self, api_key=None, max_workers=5):
        self.hai = HAI(api_key=api_key)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    def _sync_completion(self, messages, **kwargs):
        """Synchronous completion method."""
        return self.hai.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=messages,
            **kwargs
        )
    
    async def async_completion(self, messages, **kwargs):
        """Async-like completion using thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: self._sync_completion(messages, **kwargs)
        )
    
    async def batch_completions(self, message_lists: List[list], **kwargs):
        """Process multiple completions concurrently."""
        tasks = [
            self.async_completion(messages, **kwargs)
            for messages in message_lists
        ]
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def close(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)

# Usage
async def main():
    client = AsyncHAIWrapper()
    
    try:
        # Single async completion
        response = await client.async_completion([
            {"role": "user", "content": "What is emotional intelligence?"}
        ])
        print(response.choices[0].message.content)
        
        # Batch processing
        message_lists = [
            [{"role": "user", "content": "Define empathy"}],
            [{"role": "user", "content": "Define compassion"}],
            [{"role": "user", "content": "Define sympathy"}]
        ]
        
        results = await client.batch_completions(message_lists)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Request {i+1} failed: {result}")
            else:
                print(f"Request {i+1}: {result.choices[0].message.content}")
    
    finally:
        client.close()

# Run async example
# asyncio.run(main())
```

---

These examples demonstrate the full capabilities of the HelpingAI Python SDK, from basic usage to production-ready implementations. Use them as starting points for your own applications and adapt them to your specific needs.