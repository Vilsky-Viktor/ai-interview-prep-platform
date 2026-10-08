"""An interview's candidates as the company sees them: counted, listed a page at a time, sorted
and filtered in SQL by the grade and flag stored on each invite when the candidate finishes."""

import uuid
from datetime import UTC, datetime

from prepza_common import outbox
from sqlalchemy import func, select

from app.constants.events import CANDIDATE_RESCORED
from app.constants.invites import CandidateFilter, InviteStatus
from app.helpers.candidates import rescored_result
from app.helpers.search import escape_like
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.models.outbox import OutboxEvent
from app.storage.db import Session


def candidate_filters(
    interview_id, q: str, filter_by: str | None, pass_mark: int | None = None
) -> list:
    """An interview's candidates, narrowed to an email containing `q` and a status or result:
    passed (finished at or above the pass mark) or flagged (finished with integrity signals)."""
    filters = [CandidateInvite.interview_id == interview_id]

    if q:
        filters.append(CandidateInvite.email.ilike(f"%{escape_like(q.lower())}%", escape="\\"))

    if filter_by == CandidateFilter.PASSED:
        filters += [
            CandidateInvite.status == InviteStatus.FINISHED,
            CandidateInvite.grade >= pass_mark,
        ]
    elif filter_by == CandidateFilter.FLAGGED:
        filters += [CandidateInvite.status == InviteStatus.FINISHED, CandidateInvite.flagged]
    elif filter_by:
        filters.append(CandidateInvite.status == filter_by)

    return filters


def candidate_order(by_grade: bool) -> list:
    """Newest first; by grade, the best finished grade first and those without one after, each
    newest first."""
    newest = [CandidateInvite.created_at.desc(), CandidateInvite.id]

    if not by_grade:
        return newest

    return [CandidateInvite.grade.desc().nulls_last(), *newest]


async def page(
    interview_id,
    offset: int,
    limit: int,
    by_grade: bool,
    q: str = "",
    filter_by: str | None = None,
    pass_mark: int | None = None,
) -> list[CandidateInvite]:
    query = (
        select(CandidateInvite)
        .where(*candidate_filters(interview_id, q, filter_by, pass_mark))
        .order_by(*candidate_order(by_grade))
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def for_report(interview_id) -> list[CandidateInvite]:
    """Every candidate but deleted ones (they have no email to show), best grade first."""
    query = (
        select(CandidateInvite)
        .where(
            CandidateInvite.interview_id == interview_id,
            CandidateInvite.status != InviteStatus.DELETED,
        )
        .order_by(*candidate_order(True))
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def counts(interview_ids: list) -> dict:
    """Each interview's number of candidates, by id; interviews without any are missing."""
    if not interview_ids:
        return {}

    query = (
        select(CandidateInvite.interview_id, func.count())
        .where(CandidateInvite.interview_id.in_(interview_ids))
        .group_by(CandidateInvite.interview_id)
    )

    async with Session() as session:
        return {interview_id: count for interview_id, count in await session.execute(query)}


async def get(interview_id, invite_id: uuid.UUID) -> CandidateInvite | None:
    """The interview's candidate; None when the invite belongs to another interview."""
    query = select(CandidateInvite).where(
        CandidateInvite.id == invite_id, CandidateInvite.interview_id == interview_id
    )

    async with Session() as session:
        return await session.scalar(query)


async def any_finished(interview_id) -> bool:
    query = select(
        select(CandidateInvite.id)
        .where(
            CandidateInvite.interview_id == interview_id,
            CandidateInvite.status == InviteStatus.FINISHED,
        )
        .exists()
    )

    async with Session() as session:
        return bool(await session.scalar(query))


async def unscored(interview_id) -> list[uuid.UUID]:
    """Finished candidates without a stored grade: finished before grades were stored, or
    rounds didn't answer when they finished."""
    query = select(CandidateInvite.id).where(
        CandidateInvite.interview_id == interview_id,
        CandidateInvite.status == InviteStatus.FINISHED,
        CandidateInvite.grade.is_(None),
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def save_results(results: dict[uuid.UUID, tuple[int | None, bool]]) -> None:
    """Stores these candidates' (grade, flagged). Their status is left alone: only
    interview.finished marks an invite finished, as it settles the candidate's credits, so an
    invite removed before that event still gets its hold released. A finished candidate whose
    grade changes (an answer key was corrected since candidate.finished told it) is announced
    with candidate.rescored in the same transaction; the rows are locked, so of two saves at
    once (the event and the candidates list) only the first sees the change, and a repeat finds
    the grade already stored. One without a grade before (finished before grades were stored)
    is only filled in."""
    if not results:
        return

    query = (
        select(CandidateInvite, Interview)
        .join(Interview, Interview.id == CandidateInvite.interview_id)
        .where(CandidateInvite.id.in_(results), CandidateInvite.status != InviteStatus.DELETED)
        .order_by(CandidateInvite.id)
        .with_for_update(of=CandidateInvite)
    )

    async with Session() as session:
        for invite, interview in (await session.execute(query)).all():
            grade, flagged = results[invite.id]

            if invite.status == InviteStatus.FINISHED and invite.grade not in (None, grade):
                result = rescored_result(interview, invite.id, grade, flagged, datetime.now(UTC))
                outbox.add(session, OutboxEvent, CANDIDATE_RESCORED, result)

            invite.grade, invite.flagged = grade, flagged

        await session.commit()
