from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.constants.chat import Role
from app.models.conversations import Message


def history(messages: list[Message], room: int) -> list[BaseMessage]:
    """What the model reads of a conversation before a new message: the latest messages' text
    (oldest first) within `room` characters. Tools' data isn't kept: the model calls them again
    when it needs it."""
    kept: list[BaseMessage] = []

    for message in reversed(messages):
        if not message.content:
            continue

        room -= len(message.content)

        if room < 0:
            break

        kind = HumanMessage if message.role == Role.USER else AIMessage
        kept.insert(0, kind(content=message.content))

    return kept
