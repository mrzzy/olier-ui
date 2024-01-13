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
        """Convert to format suitable to be passed to OpenAI client"""
        return {"role": self.role, "content": self.content}

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary format"""
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp.isoformat()}

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
        rating: Optional. Whether the user has rated the conversation. True
            if the user rated thumbs up, False if rated thumbs down or None otherwise.
    """

    chat_log: list[Message]
    streaming_idx: Optional[int] = None
    rating: Optional[bool] = None
