from langchain_core.messages import BaseMessage
from prepza_common.llm import latest_messages

from app.constants.chat import Role
from app.models.conversations import Message


def history(messages: list[Message], room: int) -> list[BaseMessage]:
    """What the model reads of a conversation before a new message: the latest messages' text
    within `room` characters. Tools' data isn't kept: the model calls them again when it needs
    it."""
    return latest_messages([(item.role == Role.USER, item.content) for item in messages], room)
