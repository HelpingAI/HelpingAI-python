# HelpingAI

The official Python library for the [HelpingAI](https://helpingai.co) API

[![PyPI version](https://badge.fury.io/py/helpingai.svg)](https://badge.fury.io/py/helpingai)
[![Python Versions](https://img.shields.io/pypi/pyversions/helpingai.svg)](https://pypi.org/project/helpingai/)


## Installation

```bash
pip install helpingai
```

## Quick Start

First, set your API key as an environment variable:

```bash
export HAI_API_KEY='your-api-key'
```

Basic usage example:

```python
from helpingai import HAI

hai = HAI()

response = hai.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[
        {"role": "system", "content": "You are an expert in emotional intelligence."},
        {"role": "user", "content": "What makes a good leader?"}
    ]
)

print(response.choices[0].message.content)
```

## Advanced Usage

### Streaming Responses

```python
for chunk in hai.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Tell me about empathy"}],
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Advanced Parameters

```python
response = hai.chat.completions.create(
    model="HelpingAI2.5-10B",
    messages=[{"role": "user", "content": "Write a story about empathy"}],
    temperature=0.7,        # Controls randomness (0-1)
    max_tokens=500,        # Maximum length of response
    top_p=0.9,            # Nucleus sampling parameter
    frequency_penalty=0.3, # Reduces repetition
    presence_penalty=0.3   # Encourages new topics
)
```

### Robust Error Handling

```python
from helpingai import HAI, HAIError, RateLimitError, InvalidRequestError
import time

def make_completion_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return hai.chat.completions.create(
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
```

## Requirements

- Python 3.7+
- `requests` library
- Valid HelpingAI API key

## Documentation

For detailed information, check out our comprehensive documentation:

- [📚 Getting Started Guide](docs/getting_started.md)
- [📖 API Reference](docs/api_reference.md)
- [💡 Example Code](docs/examples.md)
- [❓ FAQ](docs/faq.md)

## Support

- [Submit an issue](https://github.com/HelpingAI/HelpingAI-python/issues)

