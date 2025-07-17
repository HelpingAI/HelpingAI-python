"""Base models for HAI API."""

import json
from dataclasses import dataclass, asdict, is_dataclass
from typing import Optional, Dict, Any, List, Iterator, Union
from enum import Enum

class HAIJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles BaseModel objects automatically."""
    
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.to_dict()
        elif isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

def json_dumps(obj, **kwargs):
    """JSON dumps with automatic BaseModel handling."""
    return json.dumps(obj, cls=HAIJSONEncoder, **kwargs)

class ToolCallType(str, Enum):
    """Type of tool call."""
    FUNCTION = "function"

@dataclass
class BaseModel:
    """Base class for all models."""
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        def _convert(obj: Any) -> Any:
            if is_dataclass(obj):
                return {k: _convert(v) for k, v in asdict(obj).items() if v is not None}
            elif isinstance(obj, list):
                return [_convert(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items() if v is not None}
            elif isinstance(obj, Enum):
                return obj.value
            return obj
        return _convert(self)

    def __iter__(self) -> Iterator[Any]:
        """Make models iterable for dict-like access."""
        for key, value in self.to_dict().items():
            yield key, value

    def __getitem__(self, key: str) -> Any:
        """Enable dictionary-style access."""
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in model."""
        return hasattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute with default fallback."""
        return getattr(self, key, default)

    def items(self) -> Iterator[tuple[str, Any]]:
        """Return items like a dictionary."""
        return self.to_dict().items()

    def keys(self) -> Iterator[str]:
        """Return keys like a dictionary."""
        return self.to_dict().keys()

    def values(self) -> Iterator[Any]:
        """Return values like a dictionary."""
        return self.to_dict().values()

    def json(self, **kwargs) -> str:
        """Convert to JSON string."""
        return json_dumps(self.to_dict(), **kwargs)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Pydantic-style model dump for compatibility."""
        return self.to_dict()

    def model_dump_json(self, **kwargs) -> str:
        """Pydantic-style JSON dump for compatibility."""
        return self.json(**kwargs)

    @classmethod
    def model_validate(cls, data: Union[Dict[str, Any], 'BaseModel']) -> 'BaseModel':
        """Pydantic-style validation for compatibility."""
        if isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls(**data)
        else:
            raise ValueError(f"Cannot validate {type(data)} as {cls.__name__}")

    def __json__(self):
        """JSON serialization hook for automatic conversion."""
        return self.to_dict()

    def __str__(self) -> str:
        """String representation showing the model as JSON."""
        return self.json()

    def __repr__(self) -> str:
        """Detailed representation of the model."""
        class_name = self.__class__.__name__
        fields = ', '.join(f'{k}={repr(v)}' for k, v in self.to_dict().items())
        return f'{class_name}({fields})'

@dataclass
class FunctionCall(BaseModel):
    """Function call specification."""
    name: str
    arguments: str

@dataclass
class ToolFunction(BaseModel):
    """Function specification in a tool."""
    name: str
    arguments: str

@dataclass
class ToolCall(BaseModel):
    """Tool call specification."""
    id: str
    type: str
    function: ToolFunction

@dataclass
class CompletionUsage(BaseModel):
    """Token usage information."""
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    prompt_tokens_details: Optional[Dict[str, Any]] = None

@dataclass
class ChoiceDelta(BaseModel):
    """Delta content in streaming response."""
    content: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    role: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

@dataclass
class ChatCompletionMessage(BaseModel):
    """Chat message in completion response."""
    role: str
    content: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    tool_calls: Optional[List[ToolCall]] = None

@dataclass
class Choice(BaseModel):
    """Choice in completion response."""
    index: int
    message: Optional[ChatCompletionMessage] = None
    delta: Optional[ChoiceDelta] = None
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None

@dataclass
class ChatCompletion(BaseModel):
    """Chat completion response."""
    id: str
    created: int
    model: str
    choices: List[Choice]
    object: str = "chat.completion"
    system_fingerprint: Optional[str] = None
    usage: Optional[CompletionUsage] = None

@dataclass
class ChatCompletionChunk(BaseModel):
    """Streaming chat completion response chunk."""
    id: str
    created: int
    model: str
    choices: List[Choice]
    object: str = "chat.completion.chunk"
    system_fingerprint: Optional[str] = None
