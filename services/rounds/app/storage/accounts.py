from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.helpers.export import answer_export
from app.models.certificates import Certificate
from app.models.chat import ChatMessage
from app.models.progress import QuestionProgress
from app.models.rounds import Answer, Round
from app.models.sessions import Session
from app.storage.db import Session as Db


async def delete_user(user_id: str) -> None:
    """Everything rounds holds about a user: rounds with their answers and chats, progress,
    certificates, and interview sessions with their answers and signals. Safe to repeat."""
    async with Db() as session:
        await session.execute(delete(Certificate).where(Certificate.user_id == user_id))
        await session.execute(delete(QuestionProgress).where(QuestionProgress.user_id == user_id))
        await session.execute(delete(Round).where(Round.user_id == user_id))
        await session.execute(delete(Session).where(Session.user_id == user_id))
        await session.commit()


async def export(user_id: str) -> dict:
    """The user's own data, in plain terms, for their data export."""
    async with Db() as session:
        rounds = await session.scalars(
            select(Round).where(Round.user_id == user_id).options(selectinload(Round.answers))
        )
        chats = await session.execute(
            select(
                ChatMessage.answer_id, ChatMessage.role, ChatMessage.content, ChatMessage.created_at
            )
            .join(Answer, Answer.id == ChatMessage.answer_id)
            .join(Round, Round.id == Answer.round_id)
            .where(Round.user_id == user_id)
            .order_by(ChatMessage.created_at)
        )
        certificates = await session.scalars(
            select(Certificate).where(Certificate.user_id == user_id)
        )
        sessions = await session.scalars(
            select(Session)
            .where(Session.user_id == user_id)
            .options(selectinload(Session.answers), selectinload(Session.signals))
        )

        # Each answer's follow-up chat, shown with the answer it's about.
        chat_by_answer: dict = {}

        for answer_id, role, content, created_at in chats:
            chat_by_answer.setdefault(answer_id, []).append(
                {"role": role, "content": content, "at": created_at}
            )

        return {
            "practice_rounds": [
                {
                    "topic": row.topic_title,
                    "status": row.status,
                    "final_score": row.final_score,
                    "started_at": row.started_at,
                    "finished_at": row.finished_at,
                    "answers": [
                        {
                            **answer_export(row.questions, a),
                            "tutor_chat": chat_by_answer.get(a.id, []),
                        }
                        for a in row.answers
                    ],
                }
                for row in rounds
            ],
            "certificates": [
                {
                    "id": row.id,
                    "topic": row.topic_title,
                    "score": row.score,
                    "issued_at": row.issued_at,
                }
                for row in certificates
            ],
            "interview_sections": [
                {
                    "topic": row.topic_title,
                    "status": row.status,
                    "final_score": row.final_score,
                    "started_at": row.started_at,
                    "answers": [
                        {**answer_export(row.questions, a), "seconds": a.seconds}
                        for a in row.answers
                    ],
                    "page_leaves_and_copies": [
                        {"kind": s.kind, "question_id": s.question_id, "at": s.created_at}
                        for s in row.signals
                    ],
                }
                for row in sessions
            ],
        }
