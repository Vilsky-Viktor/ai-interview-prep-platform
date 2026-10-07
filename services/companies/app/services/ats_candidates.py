import json
import logging
from uuid import UUID

from fastapi import HTTPException, status
from prepza_common.pause import refuse_if_paused
from prepza_common.user import User

from app.config.settings import settings
from app.constants.ats import (
    GREENHOUSE_STAGE_CHANGE,
    WORKABLE_MOVED,
    AtsProvider,
    CandidateStatus,
    ConnectionStatus,
    FailReason,
)
from app.constants.events import INTERVIEW_FINISHED
from app.helpers.ats import greenhouse_signed, result_comment, workable_signed
from app.helpers.notifications import ats_not_invited
from app.integrations.redis import get_redis
from app.models.ats import AtsCandidate, AtsConnection
from app.services import ats as integrations
from app.services import candidate_invites
from app.services import outbox as outbox_service
from app.storage import ats, ats_candidates, companies, interviews, invites

logger = logging.getLogger(__name__)

# Why an invite was refused, by the answer it was refused with.
REASONS = {
    status.HTTP_402_PAYMENT_REQUIRED: FailReason.CREDITS,
    status.HTTP_429_TOO_MANY_REQUESTS: FailReason.LIMIT,
    status.HTTP_503_SERVICE_UNAVAILABLE: FailReason.PAUSED,
}


async def key_of(connection: AtsConnection) -> dict | None:
    """A working connection's credentials, or None when it isn't connected or its key can't be
    read (then marked broken)."""
    if connection.status != ConnectionStatus.CONNECTED:
        return None

    try:
        return await integrations.credentials(connection)
    except HTTPException:
        return None


async def receive_workable(link_id: UUID, body: bytes, signature: str) -> None:
    """A Workable event for a linked job: a candidate moved into its stage gets the interview.
    Only events signed with the account's token count; anything for a job or link that's gone,
    or another event, is ignored, so Workable doesn't send it again."""
    found = await ats.link(link_id)

    if found is None:
        return

    link, connection = found
    key = await key_of(connection)

    if key is None:
        return

    if not workable_signed(key["token"], body, signature):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed by Workable")

    event = json.loads(body)
    candidate = event.get("data") or {}

    if (
        event.get("event_type") != WORKABLE_MOVED
        or (candidate.get("job") or {}).get("shortcode") != link.job_id
        or not candidate.get("email")
    ):
        return

    await arrived(link, connection, str(candidate["id"]), candidate["email"])


async def receive_greenhouse(connection_id: UUID, body: bytes, signature: str) -> None:
    """A Greenhouse web hook: a candidate whose application moved into a linked job's stage gets
    the interview. Only events signed with the connection's secret key count; Greenhouse's ping,
    other events, and jobs or stages not linked are ignored."""
    connection = await ats.connection_by_id(connection_id)

    if connection is None or connection.provider != AtsProvider.GREENHOUSE:
        return

    key = await key_of(connection)

    if key is None:
        return

    if not greenhouse_signed(key["webhook_secret"], body, signature):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed by Greenhouse")

    event = json.loads(body)
    application = (event.get("payload") or {}).get("application") or {}
    stage = application.get("current_stage") or {}
    candidate = application.get("candidate") or {}
    emails = [item.get("value") for item in candidate.get("email_addresses") or []]

    if event.get("action") != GREENHOUSE_STAGE_CHANGE or not any(emails):
        return

    for job in application.get("jobs") or []:
        link = await ats.link_for_job(connection.id, str(job.get("id")))

        # Its stage by id, or by name (which id Greenhouse's web hooks send isn't settled).
        if link and link.stage_id in (str(stage.get("id")), stage.get("name")):
            reference = f"{candidate.get('id')}:{application.get('id')}"
            await arrived(link, connection, reference, next(item for item in emails if item))


async def arrived(link, connection: AtsConnection, candidate_id: str, email: str) -> None:
    """A candidate the ATS sent for a linked job: saved once, then invited."""
    row = await ats_candidates.add(connection.id, link.id, link.interview_id, candidate_id, email)
    await invite(row, connection)


async def invite(row: AtsCandidate, connection: AtsConnection) -> None:
    """Invites the candidate, once: only a waiting or not-invited one, and only the request that
    claims it. An interview still being made keeps them waiting; a refused invite (credits,
    limits, the pause) is kept with its reason, to retry."""
    interview = await interviews.get(row.interview_id)

    if interview is None or interview.set_id is None:
        return

    claimed = await ats_candidates.claim(row.id, (CandidateStatus.WAITING, CandidateStatus.FAILED))

    if not claimed:
        return

    company = await companies.get(interview.company_id)
    # As if whoever connected the ATS invited them: their email limits apply.
    sender = User(uid=connection.created_by, email="", email_verified=True)

    try:
        await refuse_if_paused(get_redis())
        sent = await candidate_invites.invite(interview, company, sender, row.email)
    except HTTPException as error:
        await refused(row, interview, REASONS.get(error.status_code, FailReason.OTHER))

        return
    except Exception:
        logger.exception("Couldn't invite ATS candidate %s", row.id)
        await refused(row, interview, FailReason.OTHER)

        return

    await ats_candidates.settle(row.id, CandidateStatus.INVITED, invite_id=sent.id)
    await outbox_service.flush_quietly()


async def refused(row: AtsCandidate, interview, reason: str) -> None:
    """Kept as not invited, to retry; owners and admins hear why."""
    notice = ats_not_invited(interview, row.email, reason)
    await ats_candidates.settle(row.id, CandidateStatus.FAILED, reason, notice=notice)
    await outbox_service.flush_quietly()


async def invite_all(rows: list[AtsCandidate]) -> None:
    for row in rows:
        connection = await ats.connection_by_id(row.connection_id)

        if connection is not None:
            await invite(row, connection)


async def invite_waiting(interview_id: UUID) -> None:
    """An interview just became ready: the candidates the ATS sent for it are invited."""
    await invite_all(await ats_candidates.waiting(interview_id))


async def retry(company_id: UUID, link_id: UUID) -> None:
    """A linked job's candidates that weren't invited, or whose invite was cut off, are tried
    again (after a top-up, or once the pause is off)."""
    await invite_all(await ats_candidates.not_invited(company_id, link_id))


async def recover() -> int:
    """Daily: invites cut off midway (the server stopped) are started again; how many."""
    rows = await ats_candidates.stale()
    await invite_all(rows)

    return len(rows)


async def report(event_type: str, data: dict) -> None:
    """A candidate the ATS sent finished: their results go back to the ATS as a comment, once.
    A failing ATS raises, so the event comes again; a broken key or no member to write as
    gives up."""
    if event_type != INTERVIEW_FINISHED:
        return

    found = await ats_candidates.for_invite(UUID(data["candidate_invite_id"]))

    if found is None:
        return

    row, connection = found
    key = await key_of(connection)
    sent = await invites.get(row.invite_id)
    interview = await interviews.get(row.interview_id)
    # Workable's comments need an author; Greenhouse's notes don't.
    no_author = connection.provider == AtsProvider.WORKABLE and connection.member_id is None

    if key is None or no_author or sent is None or interview is None:
        return

    link = (
        f"{settings.site_url}/companies/{interview.company_id}/interviews/{interview.id}"
        f"/candidates/{sent.id}"
    )
    passed = sent.grade is not None and sent.grade >= interview.pass_mark
    text = result_comment(interview.title or "", sent.grade, passed, sent.flagged, link)

    try:
        await integrations.call(
            connection,
            "comment",
            candidate_id=row.candidate_id,
            member=connection.member_id,
            text=text,
        )
    except HTTPException as error:
        # A refused key was marked broken: nothing to retry. Anything else comes again.
        if error.status_code == status.HTTP_409_CONFLICT:
            return

        raise

    await ats_candidates.mark_reported(row.id)
