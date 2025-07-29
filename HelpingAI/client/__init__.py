"""HelpingAI client module.

This module provides the main client classes for interacting with the HelpingAI API.
All classes are organized into separate modules for better maintainability.
"""

from .base import BaseClient
from .completions import ChatCompletions
from .chat import Chat
from .main import HAI

# Export all public classes
__all__ = [
    "BaseClient",
    "ChatCompletions", 
    "Chat",
    "HAI"
]