from uuid import UUID

from fastapi import APIRouter
from prepza_common.auth import CurrentUser

from app.schemas.rounds import MasteredTopicOut, TopicProgressOut
from app.services.coverage import topic_progress
from app.storage import certificates, rounds

router = APIRouter(prefix="/preparations", tags=["history"])


@router.get("/mastered")
async def list_mastered_topics(user: CurrentUser) -> list[MasteredTopicOut]:
    """Topics this user has mastered, meaning earned a certificate for, on any preparation."""
    return [
        MasteredTopicOut(preparation_id=preparation_id, topic_id=topic_id)
        for preparation_id, topic_id in await certificates.mastered_topics(user.uid)
    ]


@router.get("/{preparation_id}/progress")
async def list_progress(preparation_id: UUID, user: CurrentUser) -> list[TopicProgressOut]:
    """Per topic the user has practiced: answered questions, percent correct, certificate and
    whether a round is still open."""
    certs = await certificates.for_preparation(user.uid, preparation_id)
    found = await topic_progress(user.uid, preparation_id)
    open_topics = await rounds.in_progress_topics(user.uid, preparation_id)

    return [
        TopicProgressOut(
            topic_id=topic_id,
            answered=found.get(topic_id, (0, None))[0],
            score=found.get(topic_id, (0, None))[1],
            certificate_id=certs.get(topic_id),
            in_progress=topic_id in open_topics,
        )
        for topic_id in found.keys() | certs.keys() | open_topics
    ]
