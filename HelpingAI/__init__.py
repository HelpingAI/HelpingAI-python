"""HAI API Library.

This library provides an interface to the HelpingAI API that is similar to OpenAI's Python package.

Basic usage:
    from hai import HAI
    client = HAI(api_key="your-api-key")
    
    # List available models
    models = client.models.list()
    
    # Chat completions
    response = client.chat.completions.create(
        model="HelpingAI2.5-10B",
        messages=[{"role": "user", "content": "Hello!"}]
    )

The library supports both regular and streaming responses, as well as tool/function calling.
"""

from .version import VERSION
from .client import HAI
from .error import *


__version__ = VERSION
__all__ = [
    "HAI",
    "HAIError",
    "APIError",
    "AuthenticationError",
    "InvalidRequestError",
    "RateLimitError",
    "ServiceUnavailableError",
    "APIConnectionError",
    "TimeoutError",
]
