from datetime import UTC, datetime

from prepza_common.user import User

from app.constants.rounds import RoundStatus
from app.helpers.sessions import next_session_question, seconds_left, topic_out
from app.models.sessions import Session
from app.schemas.interview_flow import InterviewStep
from app.schemas.rounds import NextQuestion
from app.services import outbox as outbox_service
from app.services.session_access import get_owned_session
from app.services.session_titles import session_out_titled
from app.storage import sessions


async def own_sections(row: Session, user: User) -> list[Session]:
    """The interview's sections, in order."""
    rows = await sessions.list_for_invite(row.candidate_invite_id)

    return [item for item in rows if item.user_id == user.uid]


async def interview_step(row: Session, user: User) -> InterviewStep:
    """The step after the last one: the first open section's waiting question, starting its
    clock. A section with no question left is finished on the way; with none open, the interview
    is done."""
    for section in await own_sections(row, user):
        if section.status != RoundStatus.IN_PROGRESS:
            continue

        # Reloaded: a question whose time ran out counts as wrong, an expired interview ends.
        section = await get_owned_session(section.id, user)

        if section.status != RoundStatus.IN_PROGRESS:
            continue

        question = next_session_question(section)

        if question is None:
            await sessions.finish(section.id)
            await outbox_service.flush_quietly()

            continue

        if section.question_shown_at is None:
            section.question_shown_at = await sessions.mark_shown(section.id)

        question.seconds_left = seconds_left(section, datetime.now(UTC))

        return await step_out(section, user, question)

    return await step_out(await sessions.get(row.id), user, None)


async def finish_interview(row: Session, user: User) -> InterviewStep:
    """The candidate ends the interview: every open section finishes; unanswered questions
    count as wrong."""
    for section in await own_sections(row, user):
        if section.status == RoundStatus.IN_PROGRESS:
            await sessions.finish(section.id)

    await outbox_service.flush_quietly()

    return await step_out(await sessions.get(row.id), user, None)


async def step_out(section: Session, user: User, question: NextQuestion | None) -> InterviewStep:
    topics = [topic_out(item) for item in await own_sections(section, user)]

    return InterviewStep(
        session=await session_out_titled(section),
        question=question,
        topics=topics,
        done=question is None and all(t.status == RoundStatus.FINISHED for t in topics),
    )
