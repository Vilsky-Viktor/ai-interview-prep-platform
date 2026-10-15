from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, status
from prepza_common.analytics import track
from prepza_common.auth import CurrentUser
from prepza_common.constants import HOUR_SECONDS
from prepza_common.paging import PageParams
from prepza_common.pause import refuse_if_paused
from prepza_common.rate_limit import hit

from app.constants.audit import AuditAction
from app.constants.interviews import PREVIEWS_PER_USER_HOUR
from app.constants.invites import INTERVIEW_NOT_READY, MAX_SEARCH_LENGTH
from app.helpers.interviews import (
    attach_set,
    attach_set_if_reachable,
    interview_out,
    session_topics,
    topics_out,
)
from app.integrations import library, rounds
from app.integrations.redis import get_redis
from app.schemas.interviews import (
    InterviewCreate,
    InterviewDetail,
    InterviewFromTemplate,
    InterviewOut,
    InterviewSettings,
    PreviewOut,
    TitleIn,
)
from app.service_auth import Via
from app.services import interview_creation, set_cache
from app.services.access import can_edit, require_company, require_editor
from app.services.candidate_billing import release_unfinished, settle_removed
from app.services.interview_access import interview_for
from app.storage import audit, candidates, interviews, invites

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_interview(
    body: InterviewCreate, company_id: UUID, user: CurrentUser
) -> InterviewOut:
    await refuse_if_paused(get_redis())
    company, _ = await require_editor(user, company_id)

    return await interview_creation.create(
        company, user.uid, user.language, body.text, body.generate_in
    )


@router.post("/from-template", status_code=status.HTTP_201_CREATED)
async def create_from_template(
    body: InterviewFromTemplate, company_id: UUID, user: CurrentUser
) -> InterviewOut:
    """A test copied from a template: free and ready at once, so no generation limits apply."""
    company, _ = await require_editor(user, company_id)
    copy = await library.copy_template(body.template_id, company.id)

    if copy is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

    interview = await interviews.create_from_template(
        company.id, copy["id"], copy["title"], copy["language"]
    )
    await track(
        "interview_from_template", user_id=user.uid, company_id=company.id, set_id=copy["id"]
    )
    # Ready at once: no generation to wait for.
    await track("test_ready", user_id=user.uid, company_id=company.id, how="template")

    return await interview_out(interview)


@router.get("")
async def list_interviews(
    company_id: UUID,
    user: CurrentUser,
    page: PageParams,
    q: Annotated[str, Query(max_length=MAX_SEARCH_LENGTH)] = "",
) -> list[InterviewOut]:
    """The company's interviews, newest first; `q` narrows them to titles containing it."""
    company, _ = await require_company(user, company_id)
    rows = await interviews.list_for_company(company.id, page.offset, page.limit, q=q.strip())
    totals = await candidates.counts([item.id for item in rows])

    return [await interview_out(item, totals.get(item.id, 0)) for item in rows]


@router.get("/{interview_id}")
async def get_interview(interview_id: UUID, user: CurrentUser) -> InterviewDetail:
    interview, _, member = await interview_for(user, interview_id)
    interview = await attach_set_if_reachable(interview)
    totals = await candidates.counts([interview.id])
    base = await interview_out(interview, totals.get(interview.id, 0))
    found = await set_cache.get_set(interview.set_id) if interview.set_id else None

    topics = topics_out(found, interview.topic_limits) if found else []

    return InterviewDetail(**base.model_dump(), topics=topics, can_edit=can_edit(member))


@router.patch("/{interview_id}/settings", status_code=status.HTTP_204_NO_CONTENT)
async def update_settings(
    interview_id: UUID, body: InterviewSettings, user: CurrentUser, via: Via
) -> None:
    interview, _, _ = await interview_for(user, interview_id, editor=True)
    await interviews.update_settings(interview.id, body)

    if body.pass_mark is not None and body.pass_mark != interview.pass_mark:
        await audit.record(
            interview.company_id, user.uid, AuditAction.PASS_MARK_CHANGED, interview.id, via=via
        )


@router.patch("/{interview_id}/title", status_code=status.HTTP_204_NO_CONTENT)
async def rename_interview(interview_id: UUID, body: TitleIn, user: CurrentUser) -> None:
    """Company owners and admins can rename an interview once it has been generated."""
    interview, _, _ = await interview_for(user, interview_id, editor=True)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, INTERVIEW_NOT_READY)

    await library.rename_set(interview.set_id, body.title)
    await interviews.set_title(interview.id, body.title)


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(interview_id: UUID, user: CurrentUser) -> None:
    """Credits, results and questions go first, so a failure leaves the interview to delete
    again."""
    interview, _, _ = await interview_for(user, interview_id, editor=True)
    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cancel the generation instead")

    # Settled while rounds still has the answers. Released again as it's removed, for an invite
    # made or sent again meanwhile; a charged candidate stays charged.
    await settle_removed(await invites.unfinished(interview.id))
    await rounds.delete_interview_data(interview.set_id)
    await library.delete_interview(interview.set_id)
    await release_unfinished(await interviews.remove(interview.id))


@router.post("/{interview_id}/preview", status_code=status.HTTP_201_CREATED)
async def preview_interview(interview_id: UUID, user: CurrentUser) -> PreviewOut:
    """A company member takes their own test as a candidate would: free, kept out of the
    candidate list, and its answers out of the questions' statistics. Each preview is new."""
    await refuse_if_paused(get_redis())
    interview, _, _ = await interview_for(user, interview_id)
    await hit(get_redis(), f"rate:previews:{user.uid}", PREVIEWS_PER_USER_HOUR, HOUR_SECONDS)
    interview = await attach_set(interview)
    content = await library.get_content(interview.set_id) if interview.set_id else None

    if content is None or not content["topics"]:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is not ready yet")

    # No invite stands behind a preview, so finishing it charges nothing.
    created = await rounds.create_sessions(
        {
            "user_id": user.uid,
            "candidate_invite_id": str(uuid4()),
            "question_seconds": interview.question_seconds,
            "topics": session_topics(interview, content),
            "preview": True,
        }
    )
    await track("interview_previewed", user_id=user.uid, company_id=interview.company_id)

    return PreviewOut(session_id=created[0]["id"])
