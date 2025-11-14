"""HAI API client with a familiar function-calling interface.

This module provides backward compatibility by importing from the new client structure.
All classes have been moved to separate modules for better maintainability.
"""

# Import all classes from the new client structure for backward compatibility
try:
    from .client.base import BaseClient
    from .client.completions import ChatCompletions
    from .client.chat import Chat
    from .client.main import HAI
except ImportError:
    # Fallback for cases where relative imports don't work
    from HelpingAI.client.base import BaseClient
    from HelpingAI.client.completions import ChatCompletions
    from HelpingAI.client.chat import Chat
    from HelpingAI.client.main import HAI

# Maintain backward compatibility - export all classes that were previously in this file
__all__ = [
    "BaseClient",
    "ChatCompletions",
    "Chat", 
    "HAI"
]