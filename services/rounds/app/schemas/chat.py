from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants.rounds import MAX_CHAT_MESSAGE_LENGTH, ChatRole


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_CHAT_MESSAGE_LENGTH)


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: ChatRole
    content: str
    created_at: datetime
