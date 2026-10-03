from uuid import UUID

from fastapi import HTTPException, status
from prepza_common.user import User

from app.helpers.coverage import coverage_score, current_scores, topic_texts
from app.helpers.scores import earns_certificate
from app.integrations import billing, library
from app.models.certificates import Certificate
from app.storage import certificates, progress, rounds


async def buy_certificate(topic_id: UUID, user: User) -> Certificate:
    """A certificate on someone else's public kit, once earned: charged and issued together.
    Certificates on the user's own and shared kits are issued when earned, for free."""
    topic = await library.get_topic_questions(topic_id, user.uid)

    if topic is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")

    if topic.public_author_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "This certificate is free")

    if await certificates.has_for_topic(user.uid, topic.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "You already have this certificate")

    texts = topic_texts(topic)
    coverage = coverage_score(
        current_scores(await progress.for_topic(user.uid, topic.id), texts), texts
    )
    latest = await rounds.latest_finished(user.uid, topic.id)

    if latest is None or not earns_certificate(coverage):
        raise HTTPException(status.HTTP_409_CONFLICT, "The certificate isn't earned yet")

    await billing.charge_certificate(
        user.uid, f"{user.uid}:{topic.id}", topic.title, topic.public_author_id
    )

    return await certificates.create(
        Certificate(
            user_id=user.uid,
            user_name=user.name or user.email,
            round_id=latest.id,
            preparation_id=topic.preparation_id,
            topic_id=topic.id,
            topic_title=topic.title,
            score=coverage,
        )
    )
