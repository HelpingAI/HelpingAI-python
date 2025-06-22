# HelpingAI Python SDK

The official Python library for the [HelpingAI](https://helpingai.co) API - Advanced AI with Emotional Intelligence

[![PyPI version](https://badge.fury.io/py/helpingai.svg)](https://badge.fury.io/py/helpingai)
[![Python Versions](https://img.shields.io/pypi/pyversions/helpingai.svg)](https://pypi.org/project/helpingai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **OpenAI-Compatible API**: Drop-in replacement with familiar interface
- **Emotional Intelligence**: Advanced AI models with emotional understanding
- **Streaming Support**: Real-time response streaming
- **Comprehensive Error Handling**: Detailed error types and retry mechanisms
- **Type Safety**: Full type hints and IDE support
- **Flexible Configuration**: Environment variables and direct initialization

## 📦 Installation

```bash
pip install HelpingAI
```

## 🔑 Authentication

Get your API key from the [HelpingAI Dashboard](https://helpingai.co/dashboard).

### Environment Variable (Recommended)

```bash
export HAI_API_KEY='your-api-key'
```

### Direct Initialization

```python
from HelpingAI import HAI

hai = HAI(api_key='your-api-key')
```

## 🎯 Quick Start

```python
from HelpingAI import HAI

# Initialize client
hai = HAI()

# Create a chat completion
response = hai.chat.completions.create(
    model="Helpingai3-raw",
    messages=[
        {"role": "system", "content": "You are an expert in emotional intelligence."},
        {"role": "user", "content": "What makes a good leader?"}
    ]
)

print(response.choices[0].message.content)
```

## 🌊 Streaming Responses

```python
# Stream responses in real-time
for chunk in hai.chat.completions.create(
    model="Helpingai3-raw",
    messages=[{"role": "user", "content": "Tell me about empathy"}],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## ⚙️ Advanced Configuration

### Parameter Control

```python
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Write a story about empathy"}],
    temperature=0.7,        # Controls randomness (0-1)
    max_tokens=500,        # Maximum length of response
    top_p=0.9,            # Nucleus sampling parameter
    frequency_penalty=0.3, # Reduces repetition
    presence_penalty=0.3,  # Encourages new topics
    hide_think=True       # Filter out reasoning blocks
)
```

### Client Configuration

```python
hai = HAI(
    api_key="your-api-key",
    base_url="https://api.helpingai.co/v1",  # Custom base URL
    timeout=30.0,                            # Request timeout
    organization="your-org-id"               # Organization ID
)
```

## 🛡️ Error Handling

```python
from HelpingAI import HAI, HAIError, RateLimitError, InvalidRequestError
import time

def make_completion_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return hai.chat.completions.create(
                model="Helpingai3-raw",
                messages=messages
            )
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(e.retry_after or 1)
        except InvalidRequestError as e:
            print(f"Invalid request: {str(e)}")
            raise
        except HAIError as e:
            print(f"API error: {str(e)}")
            raise
```

## 🤖 Available Models

### Helpingai3-raw
- **Advanced Emotional Intelligence**: Enhanced emotional understanding and contextual awareness
- **Training Data**: 15M emotional dialogues, 3M therapeutic exchanges, 250K cultural conversations, 1M crisis response scenarios
- **Best For**: AI companionship, emotional support, therapy guidance, personalized learning

### Dhanishtha-2.0-preview
- **World's First Intermediate Thinking Model**: Multi-phase reasoning with self-correction capabilities
- **Unique Features**: `<think>...</think>` blocks for transparent reasoning, structured emotional reasoning (SER)
- **Best For**: Complex problem-solving, analytical tasks, educational content, reasoning-heavy applications

```python
# List all available models
models = hai.models.list()
for model in models:
    print(f"Model: {model.id} - {model.description}")

# Get specific model info
model = hai.models.retrieve("Helpingai3-raw")
print(f"Model: {model.name}")

# Use Dhanishtha-2.0 for complex reasoning
response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Solve this step by step: What's 15% of 240?"}],
    hide_think=False  # Show reasoning process
)
```

## 📚 Documentation

Comprehensive documentation is available:

- [📖 Getting Started Guide](docs/getting_started.md) - Installation and basic usage
- [🔧 API Reference](docs/api_reference.md) - Complete API documentation
- [💡 Examples](docs/examples.md) - Code examples and use cases
- [❓ FAQ](docs/faq.md) - Frequently asked questions

## 🏗️ Project Structure

```
HelpingAI-python/
├── HelpingAI/              # Main package
│   ├── __init__.py         # Package initialization
│   ├── client.py           # Main HAI client
│   ├── models.py           # Model management
│   ├── base_models.py      # Data models
│   ├── error.py            # Exception classes
│   └── version.py          # Version information
├── docs/                   # Documentation
├── tests/                  # Test suite
├── setup.py               # Package configuration
└── README.md              # This file
```

## 🔧 Requirements

- **Python**: 3.7-3.14
- **Dependencies**: 
  - `requests` - HTTP client
  - `typing_extensions` - Type hints support

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

- **Issues**: [GitHub Issues](https://github.com/HelpingAI/HelpingAI-python/issues)
- **Documentation**: [HelpingAI Docs](https://helpingai.co/docs)
- **Dashboard**: [HelpingAI Dashboard](https://helpingai.co/dashboard)
- **Email**: varun@helpingai.co

## 🚀 What's New in v1.1.0

- **Extended Python Support**: Now supports Python 3.7-3.14
- **Updated Models**: Support for latest models (Helpingai3-raw, Dhanishtha-2.0-preview)
- **Dhanishtha-2.0 Integration**: World's first intermediate thinking model with multi-phase reasoning
- **HelpingAI3 Support**: Enhanced emotional intelligence with advanced contextual awareness
- **Improved Model Management**: Better fallback handling and detailed model descriptions
- **OpenAI-Compatible Interface**: Familiar API design
- **Enhanced Error Handling**: Comprehensive exception types
- **Streaming Support**: Real-time response streaming
- **Advanced Filtering**: Hide reasoning blocks with `hide_think` parameter

---

**Built with ❤️ by the HelpingAI Team**

*Empowering AI with Emotional Intelligence*