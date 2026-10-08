from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.constants.chat import (
    HISTORY_MESSAGES,
    MAX_MESSAGE_LENGTH,
    MAX_PAGE_LENGTH,
    QUESTION_TOO_LONG,
    Role,
    Source,
)
from app.constants.welcome import Stage


class EarlierTurn(BaseModel):
    """A message from before the user signed in (the panel's visitor chat), cut to the length a
    message may have."""

    role: Role
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def cut(cls, content: str) -> str:
        return content[:MAX_MESSAGE_LENGTH]


class ChatRequest(BaseModel):
    """A new message: in a conversation, or starting one. `company_id`: the company picked in
    the panel (none: all companies), which this message is about; a new conversation is listed
    under it. `page` is the page's path, only as context. `earlier`: the chat the user
    had before signing in, saved first into a new conversation (ignored in an existing one)."""

    conversation_id: UUID | None = None
    company_id: UUID | None = None
    message: str = Field(min_length=1)
    source: Source = Source.TEXT
    page: str | None = Field(default=None, max_length=MAX_PAGE_LENGTH)
    earlier: list[EarlierTurn] = Field(default_factory=list, max_length=HISTORY_MESSAGES)

    @field_validator("message")
    @classmethod
    def short_enough(cls, message: str) -> str:
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError(QUESTION_TOO_LONG)

        return message


class ConfigOut(BaseModel):
    """The limits the panel shows and keeps to."""

    max_message_length: int
    max_audio_seconds: int
    messages_per_hour: int
    messages_per_day: int


class WelcomeOut(BaseModel):
    stage: Stage
