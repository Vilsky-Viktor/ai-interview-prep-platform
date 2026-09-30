from uuid import UUID

from fastapi import APIRouter

from app.auth import CurrentUser
from app.schemas.rounds import MasteredTopicOut, TopicPassOut
from app.services.coverage import answered_counts
from app.storage import certificates, rounds

router = APIRouter(prefix="/preparations", tags=["history"])


@router.get("/mastered")
async def list_mastered_topics(user: CurrentUser) -> list[MasteredTopicOut]:
    """Topics this user has mastered, meaning earned a certificate for, on any preparation."""
    return [
        MasteredTopicOut(preparation_id=preparation_id, topic_id=topic_id)
        for preparation_id, topic_id in await certificates.mastered_topics(user.uid)
    ]


@router.get("/{preparation_id}/passes")
async def list_passes(preparation_id: UUID, user: CurrentUser) -> list[TopicPassOut]:
    """Best finished score per topic and mode on this preparation."""
    certs = await certificates.for_preparation(user.uid, preparation_id)
    answered = await answered_counts(user.uid, preparation_id)

    return [
        TopicPassOut(
            topic_id=topic_id,
            mode=mode,
            score=score,
            answered=answered.get((topic_id, mode), 0),
            certificate_id=certs.get(topic_id),
        )
        for topic_id, mode, score in await rounds.best_for_preparation(
            user.uid, preparation_id
        )
    ]
