from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser
from prepza_common.constants import MAX_GOAL_LENGTH

from app.constants.ats import AtsProvider, CandidateStatus
from app.helpers.ats import job_text, workable_subdomain
from app.integrations import workable
from app.schemas.ats import (
    AtsItemOut,
    ConnectionOut,
    IntegrationsOut,
    JobLinkIn,
    JobLinkOut,
    JobTextOut,
    WorkableIn,
)
from app.services import ats as integrations
from app.services import ats_candidates as ats_candidates_service
from app.services.access import require_company, require_editor
from app.storage import ats, ats_candidates, interviews

router = APIRouter(prefix="/ats", tags=["ats"])


@router.get("")
async def list_connections(company_id: UUID, user: CurrentUser) -> IntegrationsOut:
    """The company's ATS connections; every member sees them, only owners and admins change
    them."""
    await require_company(user, company_id)
    rows = await ats.connections(company_id)

    return IntegrationsOut(
        available=integrations.available(),
        connections=[
            ConnectionOut(
                provider=row.provider,
                account=row.account,
                status=row.status,
                created_at=row.created_at,
            )
            for row in rows
        ],
    )


@router.put("/workable", status_code=status.HTTP_204_NO_CONTENT)
async def connect_workable(company_id: UUID, body: WorkableIn, user: CurrentUser) -> None:
    """Connects Workable with an account's API access token, checked with one read first. A
    second connect replaces the key."""
    await require_editor(user, company_id)
    integrations.require_available()
    subdomain = workable_subdomain(body.account)

    if subdomain is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Enter your Workable address, like acme.workable.com"
        )

    token = body.token.strip()

    try:
        await workable.check(subdomain, token)
    except workable.KeyRejected:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Workable didn't accept this token for that account"
        ) from None

    credentials = integrations.seal({"subdomain": subdomain, "token": token})
    # Who results are written back as: the connecting user's Workable member, or an admin.
    member = await workable.member_id(subdomain, token, user.email)
    await ats.connect(company_id, AtsProvider.WORKABLE, subdomain, credentials, user.uid, member)


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect(company_id: UUID, provider: AtsProvider, user: CurrentUser) -> None:
    """Disconnects: Workable's notifications are cancelled, then the key is deleted, and its
    linked jobs with it."""
    await require_editor(user, company_id)
    connection = await ats.connection(company_id, provider)

    if connection is not None:
        await integrations.unsubscribe(connection, await ats.subscriptions(company_id))

    await ats.disconnect(company_id, provider)


@router.get("/{provider}/jobs")
async def list_jobs(company_id: UUID, provider: AtsProvider, user: CurrentUser) -> list[AtsItemOut]:
    await require_editor(user, company_id)
    connection = await integrations.connected(company_id, provider)

    return [AtsItemOut(**job) for job in await integrations.jobs(connection)]


@router.get("/{provider}/jobs/{job_id}/stages")
async def list_stages(
    company_id: UUID, provider: AtsProvider, job_id: str, user: CurrentUser
) -> list[AtsItemOut]:
    await require_editor(user, company_id)
    connection = await integrations.connected(company_id, provider)

    return [AtsItemOut(**stage) for stage in await integrations.stages(connection, job_id)]


@router.get("/{provider}/jobs/{job_id}/text")
async def job_text_of(
    company_id: UUID, provider: AtsProvider, job_id: str, user: CurrentUser
) -> JobTextOut:
    """A job's title, description, requirements and benefits as plain text, to make an
    interview from (the same limit as a pasted job description)."""
    await require_editor(user, company_id)
    connection = await integrations.connected(company_id, provider)
    found = await integrations.job(connection, job_id)

    return JobTextOut(text=job_text(found["name"], found["sections"], MAX_GOAL_LENGTH))


@router.get("/links")
async def list_links(company_id: UUID, user: CurrentUser) -> list[JobLinkOut]:
    await require_company(user, company_id)
    counts = await ats_candidates.counts(company_id)

    return [
        JobLinkOut(
            id=link.id,
            provider=provider,
            job_name=link.job_name,
            stage_name=link.stage_name,
            interview_id=link.interview_id,
            interview_title=title,
            invited=counts.get(link.id, {}).get(CandidateStatus.INVITED, 0),
            # Including an invite underway: one cut off midway shows here to invite again.
            not_invited=counts.get(link.id, {}).get(CandidateStatus.FAILED, 0)
            + counts.get(link.id, {}).get(CandidateStatus.INVITING, 0),
            waiting=counts.get(link.id, {}).get(CandidateStatus.WAITING, 0),
        )
        for link, provider, title in await ats.links(company_id)
    ]


@router.post("/links", status_code=status.HTTP_201_CREATED)
async def add_link(company_id: UUID, body: JobLinkIn, user: CurrentUser) -> None:
    """Links an ATS job to one of the company's interviews: its candidates who reach the stage
    will get the interview. A job has one interview."""
    await require_editor(user, company_id)
    connection = await integrations.connected(company_id, body.provider)
    interview = await interviews.get(body.interview_id)

    # Also an interview still being made, as "new interview from this job" links it at once;
    # candidates are invited once it's ready.
    if interview is None or interview.company_id != company_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")

    # The names as the ATS has them now, which also checks the job and stage exist.
    job = next(
        (job for job in await integrations.jobs(connection) if job["id"] == body.job_id), None
    )
    stage_list = await integrations.stages(connection, body.job_id) if job else []
    stage = next((stage for stage in stage_list if stage["id"] == body.stage_id), None)

    if job is None or stage is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That job or stage isn't in Workable")

    link_id = await ats.add_link(connection.id, interview.id, job, stage)

    if link_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "That job is already linked")

    # Workable then sends candidates moved into the stage; a link it won't notify isn't kept.
    try:
        subscription = await integrations.subscribe(connection, link_id, job["id"], stage["id"])
    except Exception:
        await ats.remove_link(company_id, link_id)
        raise

    await ats.set_subscription(link_id, subscription)


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_link(company_id: UUID, link_id: UUID, user: CurrentUser) -> None:
    await require_editor(user, company_id)
    found = await ats.link(link_id)

    if found is not None and found[1].company_id == company_id:
        await integrations.unsubscribe(found[1], await ats.subscriptions(company_id, link_id))

    if not await ats.remove_link(company_id, link_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Link not found")


@router.post("/links/{link_id}/retry", status_code=status.HTTP_204_NO_CONTENT)
async def retry_candidates(company_id: UUID, link_id: UUID, user: CurrentUser) -> None:
    """Invites again the candidates the ATS sent for this job who weren't invited (after a
    top-up, or once the pause is off)."""
    await require_editor(user, company_id)
    await ats_candidates_service.retry(company_id, link_id)
