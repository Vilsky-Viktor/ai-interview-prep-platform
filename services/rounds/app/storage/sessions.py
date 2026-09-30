import random
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.constants.rounds import RoundStatus
from app.helpers.scores import candidate_progress, interview_finished
from app.models.rounds import Answer
from app.models.sessions import Session
from app.schemas.library import TopicQuestions
from app.storage.db import Session as Db

LOAD_SESSION = [selectinload(Session.answers)]


async def create_many(
    user_id: str,
    candidate_invite_id: uuid.UUID,
    mode: str,
    share_results: bool,
    topics: list[TopicQuestions],
) -> list[Session]:
    rows = [
        Session(
            user_id=user_id,
            topic_id=topic.id,
            interview_set_id=topic.preparation_id,
            candidate_invite_id=candidate_invite_id,
            topic_title=topic.title,
            mode=mode,
            share_results=share_results,
            status=RoundStatus.IN_PROGRESS,
            questions=[question.model_dump(mode="json") for question in topic.questions],
            final_score=None,
            finished_at=None,
            answers=[],
        )
        for topic in topics
    ]

    for row in rows:
        random.shuffle(row.questions)

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


async def add_answer(answer: Answer) -> bool:
    async with Db() as session:
        session.add(answer)

        try:
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
