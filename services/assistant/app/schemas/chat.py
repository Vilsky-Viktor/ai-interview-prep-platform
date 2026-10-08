from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.constants.chat import MAX_MESSAGE_LENGTH, MAX_PAGE_LENGTH, QUESTION_TOO_LONG, Source


class ChatRequest(BaseModel):
    """A new message: in a conversation, or starting one about the company of the page the user
    is on (or none). `page` is that page's path, only as context."""

    conversation_id: UUID | None = None
    company_id: UUID | None = None
    message: str = Field(min_length=1)
    source: Source = Source.TEXT
    page: str | None = Field(default=None, max_length=MAX_PAGE_LENGTH)

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
