import json

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from app.constants.chat import Role
from app.models.conversations import Message, ToolCall


def history(rows: list[tuple[Message, list[ToolCall]]], room: int) -> list[BaseMessage]:
    """What the model reads of a conversation before a new message: the latest messages (oldest
    first) within `room` characters. An answer brings the tools' results it read while they fit,
    and only its text once they don't."""
    kept: list[list[BaseMessage]] = []

    for message, calls in reversed(rows):
        results = [json.dumps(call.result, ensure_ascii=False) for call in calls]
        size = len(message.content) + sum(len(result) for result in results)

        if size > room:
            calls, results, size = [], [], len(message.content)

        if size > room:
            break

        room -= size
        kept.insert(0, as_messages(message, calls, results))

    return [item for messages in kept for item in messages]


def as_messages(message: Message, calls: list[ToolCall], results: list[str]) -> list[BaseMessage]:
    """A stored message as the model's messages: an answer's tool calls, all in one step, with
    their results, then its text."""
    if message.role == Role.USER:
        return [HumanMessage(content=message.content)]

    found: list[BaseMessage] = []

    if calls:
        found.append(
            AIMessage(
                content="",
                tool_calls=[
                    {"name": call.tool, "args": call.arguments, "id": str(call.id)}
                    for call in calls
                ],
            )
        )
        found += [
            ToolMessage(content=result, tool_call_id=str(call.id))
            for call, result in zip(calls, results, strict=True)
        ]

    if message.content:
        found.append(AIMessage(content=message.content))

    return found
