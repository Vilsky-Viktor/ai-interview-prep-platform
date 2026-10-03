import random
import uuid
from datetime import UTC, datetime

from prepza_common import outbox
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.constants.integrity import IntegritySignal
from app.constants.rounds import RoundStatus
from app.helpers.scores import candidate_progress, interview_finished
from app.models.outbox import OutboxEvent
from app.models.rounds import Answer
from app.models.sessions import Session
from app.models.signals import Signal
from app.schemas.library import TopicQuestions
from app.storage.db import Session as Db

LOAD_SESSION = [selectinload(Session.answers), selectinload(Session.signals)]


async def create_many(
    user_id: str,
    candidate_invite_id: uuid.UUID,
    topics: list[TopicQuestions],
    question_seconds: int,
) -> list[Session]:
    rows = [
        Session(
            user_id=user_id,
            topic_id=topic.id,
            interview_set_id=topic.preparation_id,
            candidate_invite_id=candidate_invite_id,
            topic_title=topic.title,
            status=RoundStatus.IN_PROGRESS,
            questions=[question.model_dump(mode="json") for question in topic.questions],
            final_score=None,
            finished_at=None,
            question_seconds=question_seconds,
            answers=[],
        )
        for topic in topics
    ]

    # Each candidate gets their own question and option order, so answers can't be passed on.
    for row in rows:
        random.shuffle(row.questions)

        for question in row.questions:
            random.shuffle(question["options"])

    async with Db() as session:
        session.add_all(rows)
        await session.commit()

    return rows


async def get(session_id: uuid.UUID) -> Session | None:
    async with Db() as session:
        return await session.get(Session, session_id, options=LOAD_SESSION)


async def list_for_invite(candidate_invite_id: uuid.UUID) -> list[Session]:
    query = (
        select(Session)
        .where(Session.candidate_invite_id == candidate_invite_id)
        .options(*LOAD_SESSION)
        .order_by(Session.started_at)
    )

    async with Db() as session:
        return list(await session.scalars(query))


async def scores_for_invites(
    invite_ids: list[uuid.UUID],
) -> dict[uuid.UUID, tuple[int, int | None, bool]]:
    if not invite_ids:
        return {}

    query = (
        select(Session)
        .where(Session.candidate_invite_id.in_(invite_ids))
        .options(selectinload(Session.answers))
    )

    async with Db() as session:
        rows = list(await session.scalars(query))

    grouped: dict[uuid.UUID, list[Session]] = {}

    for row in rows:
        grouped.setdefault(row.candidate_invite_id, []).append(row)

    result = {}

    for invite_id, topics in grouped.items():
        scores = [answer.score for topic in topics for answer in topic.answers]
        total = sum(len(topic.questions) for topic in topics)
        progress, grade = candidate_progress(scores, total)
        result[invite_id] = (
            progress,
            grade,
            interview_finished([topic.status for topic in topics]),
        )

    return result


async def mark_shown(session_id: uuid.UUID) -> datetime:
    """Starts the clock on the waiting question; reloading the page doesn't restart it."""
    now = datetime.now(UTC)

    async with Db() as session:
        await session.execute(
            update(Session)
            .where(Session.id == session_id, Session.question_shown_at.is_(None))
            .values(question_shown_at=now)
        )
        await session.commit()

    return now


async def add_signal(
    session_id: uuid.UUID, question_id: uuid.UUID | None, kind: IntegritySignal
) -> None:
    async with Db() as session:
        session.add(Signal(session_id=session_id, question_id=question_id, kind=kind))
        await session.commit()


async def add_answer(answer: Answer, event: tuple[str, dict] | None = None) -> bool:
    """Saves the answer (and its event, when it has one) and stops the clock, so the next
    question starts its own. A question that timed out has no event: nothing was picked.

    False when the question already has an answer, e.g. two requests timing out the same
    question at once.
    """
    async with Db() as session:
        session.add(answer)

        if event:
            outbox.add(session, OutboxEvent, *event)

        try:
            await session.flush()
            await session.execute(
                update(Session)
                .where(Session.id == answer.session_id)
                .values(question_shown_at=None)
            )
            await session.commit()
        except IntegrityError:
            return False

    return True


async def finish(session_id: uuid.UUID, final_score: int) -> None:
    async with Db() as session:
        await session.execute(
            update(Session)
            .where(Session.id == session_id, Session.status == RoundStatus.IN_PROGRESS)
            .values(
                status=RoundStatus.FINISHED,
                final_score=final_score,
                finished_at=datetime.now(UTC),
            )
        )
        await session.commit()


async def remove_for_invites(candidate_invite_ids: list[uuid.UUID]) -> None:
    """Deletes the candidates' sessions; answers and signals cascade."""
    if not candidate_invite_ids:
        return

    async with Db() as session:
        await session.execute(
            delete(Session).where(Session.candidate_invite_id.in_(candidate_invite_ids))
        )
        await session.commit()


async def remove_for_interview(interview_set_id: uuid.UUID) -> None:
    """Deletes every candidate's sessions on the interview; answers and chats cascade."""
    async with Db() as session:
        await session.execute(delete(Session).where(Session.interview_set_id == interview_set_id))
        await session.commit()
