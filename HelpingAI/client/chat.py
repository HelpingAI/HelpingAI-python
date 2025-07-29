"""Chat API interface for the HelpingAI client.

Access chat completions via the `completions` property.
"""

from typing import TYPE_CHECKING

from .completions import ChatCompletions

if TYPE_CHECKING:
    from .main import HAI


class Chat:
    """Chat API interface for the HelpingAI client.

    Access chat completions via the `completions` property.
    """
    def __init__(self, client: "HAI") -> None:
        self.completions: ChatCompletions = ChatCompletions(client)