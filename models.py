#
# Olier
# Frontend
#

from dataclasses import InitVar, dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Message:
    """A Chat Message between between the user and assistant."""

    role: str
    content: str
    timestamp: datetime = field(init=False)
    logged_on: InitVar[Optional[datetime]] = None

    def __post_init__(self, logged_on: Optional[datetime]):
        # __setattr__ needed as Message is a 'frozen' dataclass
        object.__setattr__(
            self, "timestamp", datetime.now() if logged_on is None else logged_on
        )

    @property
    def id(self) -> str:
        """Identifier that uniquely identifies this message."""
        return str(hash(self))

    def append(self, content: str) -> "Message":
        """Append the given content to the message's content"""
        return Message(self.role, self.content + content, self.timestamp)

    def to_openai(self) -> dict[str, str]:
        """Convert format suitable to pass to OpenAI client"""
        return {"role": self.role, "content": self.content}

    def __str__(self) -> str:
        """Formats & returns Message as a text format:

        [<role> @ <timestamp>]
        <content ...>
        """
        return f"[{self.role} @ {self.timestamp.isoformat()}]\n{self.content}"


@dataclass
class State:
    """
    Encapsulates the rendering state of the Olier Frontend UI.

    Attributes:
        chat_log: Chat log of messages between the user & chatbot to render.
        streaming_idx: Optional. Index of the user message the UI is currently streaming
            the Chatbot's reply to or None if not currently streaming.
        is_copying: Optional. Whether the user is currently copying from the clipboard.
    """

    chat_log: list[Message]
    streaming_idx: Optional[int] = None
    is_copying: bool = False
