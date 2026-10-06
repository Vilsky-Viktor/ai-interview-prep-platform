from fastapi import HTTPException, status

from app.helpers.candidates import candidate_seconds
from app.helpers.interviews import attach_set, session_topics
from app.integrations import library, rounds
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.schemas.invites import InviteStartOut, SessionSummary
from app.storage import invites


async def start_sessions(
    invite: CandidateInvite, interview: Interview, user_id: str
) -> InviteStartOut:
    """Starts (or returns) the candidate's sessions: one per topic, with fresh random questions."""
    interview = await attach_set(interview)

    if interview.set_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview is not ready yet")

    content = await library.get_content(interview.set_id)

    if content is None or not content["topics"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview content not found")

    await invites.start(invite, user_id)
    created = await rounds.create_sessions(
        {
            "user_id": user_id,
            "candidate_invite_id": str(invite.id),
            "question_seconds": candidate_seconds(interview.question_seconds, invite.extra_time),
            "topics": session_topics(interview, content),
        }
    )

    return InviteStartOut(
        sessions=[
            SessionSummary(id=row["id"], topic_title=row["topic_title"], status=row["status"])
            for row in created
        ]
    )
