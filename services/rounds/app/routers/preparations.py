from uuid import UUID

from fastapi import APIRouter
from prepza_common.auth import CurrentUser

from app.helpers.scores import score_passed
from app.integrations import library
from app.schemas.rounds import TopicProgressOut
from app.services.coverage import topic_progress
from app.storage import certificates, rounds

router = APIRouter(prefix="/preparations", tags=["history"])


@router.get("/{preparation_id}/progress")
async def list_progress(preparation_id: UUID, user: CurrentUser) -> list[TopicProgressOut]:
    """Per topic the user has practiced: answered questions, percent correct, certificate and
    whether a round is still open."""
    certs = await certificates.for_preparation(user.uid, preparation_id)
    found = await topic_progress(user.uid, preparation_id)
    open_topics = await rounds.in_progress_topics(user.uid, preparation_id)
    question_set = await library.get_set(preparation_id)
    totals = {
        UUID(topic["id"]): topic["question_count"]
        for topic in (question_set or {}).get("topics", [])
    }
    rows = []

    for topic_id in found.keys() | certs.keys() | open_topics:
        answered, score = found.get(topic_id, (0, None))
        complete = answered >= totals.get(topic_id, 0) > 0
        rows.append(
            TopicProgressOut(
                topic_id=topic_id,
                answered=answered,
                score=score,
                complete=complete,
                passed=topic_id in certs or (complete and bool(score_passed(score))),
                certificate_id=certs.get(topic_id),
                in_progress=topic_id in open_topics,
            )
        )

    return rows
