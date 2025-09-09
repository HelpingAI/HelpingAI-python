"""HAI API client with OpenAI-like interface.

This module provides backward compatibility by importing from the new client structure.
All classes have been moved to separate modules for better maintainability.
"""

# Import all classes from the new client structure for backward compatibility
from client.base import BaseClient
from client.completions import ChatCompletions
from client.chat import Chat
from client.main import HAI

# Maintain backward compatibility - export all classes that were previously in this file
__all__ = [
    "BaseClient",
    "ChatCompletions",
    "Chat", 
    "HAI"
]