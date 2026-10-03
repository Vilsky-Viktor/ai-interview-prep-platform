from fastapi import APIRouter, HTTPException, status
from prepza_common.auth import CurrentUser

from app.constants.invites import InviteStatus
from app.helpers.interviews import attach_set, interview_title, pick_questions
from app.integrations import library, rounds
from app.schemas.invites import InviteStartOut, InviteView, SessionSummary
from app.storage import companies
from app.storage import invites as invite_store

router = APIRouter(prefix="/invites", tags=["invites"])


@router.get("/{token}")
async def get_invite(token: str, user: CurrentUser) -> InviteView:
    found = await invite_store.get_by_token(token)

    # An expired invite's link stops working until the company sends it again.
    if found is None or found[0].status == InviteStatus.EXPIRED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    invite, interview = found
    interview = await attach_set(interview)
    title = await interview_title(interview)

    company = await companies.get(interview.company_id)

    return InviteView(
        interview_id=interview.id,
        title=title,
        company=company.name if company else "",
        email=invite.email,
        status=invite.status,
        question_seconds=interview.question_seconds,
    )


@router.post("/{token}/start")
async def start_invite(token: str, user: CurrentUser) -> InviteStartOut:
    """Only the invited, verified email can start; a forwarded link is useless to anyone else."""
    found = await invite_store.get_by_token(token)

    if found is None or found[0].status == InviteStatus.EXPIRED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")

    invite, interview = found

    if not user.email_verified or user.email.lower() != invite.email:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This invite was sent to a different email address"
        )

    if invite.status == InviteStatus.FINISHED:
        raise HTTPException(status.HTTP_409_CONFLICT, "This interview is already finished")

    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is not ready yet")

    content = await library.get_content(interview.set_id)

    if content is None or not content["topics"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview content not found")

    await invite_store.start(invite, user.uid)
    created = await rounds.create_sessions(
        {
            "user_id": user.uid,
            "candidate_invite_id": str(invite.id),
            "question_seconds": interview.question_seconds,
            "topics": [
                {
                    "id": topic["id"],
                    "preparation_id": content["id"],
                    "title": topic["title"],
                    "questions": pick_questions(
                        topic["questions"], interview.topic_limits.get(str(topic["id"]))
                    ),
                }
                for topic in content["topics"]
            ],
        }
    )

    return InviteStartOut(
        sessions=[
            SessionSummary(
                id=row["id"],
                topic_title=row["topic_title"],
                status=row["status"],
            )
            for row in created
        ]
    )
