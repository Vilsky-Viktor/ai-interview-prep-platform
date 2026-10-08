from datetime import timedelta
from uuid import UUID

from sqlalchemy import select, update

from app.constants.chat import Role, Source, Status, ToolState
from app.models.answers import Answer
from app.models.conversations import Conversation, Message, ToolCall, now
from app.storage.db import Session


async def add_question(conversation_id: UUID, content: str, source: Source) -> Message:
    """The user's message; the conversation isn't idle from now."""
    async with Session() as session:
        message = Message(
            conversation_id=conversation_id, role=Role.USER, source=source, content=content
        )
        session.add(message)
        await _touch(session, conversation_id)
        await session.commit()

        return message


async def add_earlier(conversation_id: UUID, turns: list) -> None:
    """Messages from before the user signed in, in their order, at the start of a new
    conversation."""
    async with Session() as session:
        start = now()

        for index, turn in enumerate(turns):
            session.add(
                Message(
                    conversation_id=conversation_id,
                    role=turn.role,
                    source=Source.TEXT,
                    content=turn.content,
                    created_at=start + timedelta(microseconds=index),
                )
            )

        await session.commit()


async def add_answer(conversation_id: UUID, answer: Answer, status: Status) -> UUID:
    """The assistant's answer with the tools it called (their trimmed results, which later turns
    read again); its id."""
    async with Session() as session:
        message = Message(
            conversation_id=conversation_id,
            role=Role.ASSISTANT,
            content=answer.content,
            blocks=answer.blocks,
            status=status,
            input_tokens=answer.input_tokens,
            output_tokens=answer.output_tokens,
        )
        session.add(message)
        await session.flush()

        for result in answer.results:
            session.add(
                ToolCall(
                    message_id=message.id,
                    tool=result.tool,
                    arguments=result.arguments,
                    status_code=result.status_code,
                    duration_ms=result.duration_ms,
                    result=result.content,
                    state=ToolState.DONE if result.succeeded else ToolState.FAILED,
                )
            )

        await _touch(session, conversation_id)
        await session.commit()

        return message.id


async def _touch(session, conversation_id: UUID) -> None:
    await session.execute(
        update(Conversation).where(Conversation.id == conversation_id).values(updated_at=now())
    )


async def recent(conversation_id: UUID, limit: int) -> list[tuple[Message, list[ToolCall]]]:
    """The latest `limit` messages, oldest first, each with the tools it called."""
    async with Session() as session:
        messages = list(
            await session.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc(), Message.id)
                .limit(limit)
            )
        )
        calls = await session.scalars(
            select(ToolCall)
            .where(ToolCall.message_id.in_([message.id for message in messages]))
            .order_by(ToolCall.created_at, ToolCall.id)
        )

    by_message: dict[UUID, list[ToolCall]] = {}

    for call in calls:
        by_message.setdefault(call.message_id, []).append(call)

    return [(message, by_message.get(message.id, [])) for message in reversed(messages)]


async def of_conversation(conversation_id: UUID) -> list[Message]:
    async with Session() as session:
        return list(
            await session.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at, Message.id)
            )
        )


async def export(user_id: str) -> list[dict]:
    """The user's conversations with their messages, oldest first; never the tools' results,
    which are their companies' data, not theirs."""
    async with Session() as session:
        conversations = list(
            await session.scalars(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.created_at, Conversation.id)
            )
        )
        messages = await session.scalars(
            select(Message)
            .where(Message.conversation_id.in_([item.id for item in conversations]))
            .order_by(Message.created_at, Message.id)
        )

    by_conversation: dict[UUID, list[dict]] = {}

    for message in messages:
        by_conversation.setdefault(message.conversation_id, []).append(
            {
                "role": message.role,
                "source": message.source,
                "content": message.content,
                "status": message.status,
                "at": message.created_at,
            }
        )

    return [
        {
            "company_id": conversation.company_id,
            "title": conversation.title,
            "at": conversation.created_at,
            "messages": by_conversation.get(conversation.id, []),
        }
        for conversation in conversations
    ]
