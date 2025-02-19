"""Base models for HAI API."""

from dataclasses import dataclass, asdict, is_dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum

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

    def __iter__(self):
        """Make models iterable for dict-like access."""
        for key, value in self.to_dict().items():
            yield key, value

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
