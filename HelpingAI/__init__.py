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

from .base_models import *
from .models import *

# New tool utilities
try:
    from .tools import (
        Fn, tools, get_tools, get_tools_format,
        ToolRegistry, ToolExecutionError, SchemaValidationError,
        ToolRegistrationError, SchemaGenerationError
    )
    _TOOLS_AVAILABLE = True
except ImportError:
    _TOOLS_AVAILABLE = False


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
    # Expose base models and Model
    "BaseModel",
    "ChatCompletion",
    "ChatCompletionChunk",
    "ChatCompletionMessage",
    "Choice",
    "ChoiceDelta",
    "CompletionUsage",
    "ToolCall",
    "ToolFunction",
    "FunctionCall",
    "Model",
    "Models",
    # JSON utilities
    "HAIJSONEncoder",
    "json_dumps",
    "ToolCallType",
]

# Add tool utilities to __all__ if available
if _TOOLS_AVAILABLE:
    __all__.extend([
        # New tool utilities
        "Fn",
        "tools",
        "get_tools",
        "get_tools_format",
        "ToolRegistry",
        "ToolExecutionError",
        "SchemaValidationError",
        "ToolRegistrationError",
        "SchemaGenerationError",
    ])
