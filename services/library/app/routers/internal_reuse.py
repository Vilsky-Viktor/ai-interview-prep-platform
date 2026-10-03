from fastapi import APIRouter, Query, status

from app.constants.reuse import MAX_EMBEDDING_BATCH
from app.schemas.reuse import ReusedQuestion, ReuseIn, TopicEmbedding, TopicToEmbed
from app.service_auth import ServiceCaller
from app.storage import reuse

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/reuse")
async def find_reusable(body: ReuseIn, caller: ServiceCaller) -> list[ReusedQuestion]:
    """Proven questions from public preparations on a similar topic, for a new generation."""
    found = await reuse.find(body.embedding, body.level, body.language, body.count)

    return [ReusedQuestion(text=text, options=options) for text, options in found]


@router.get("/embeddings/missing")
async def list_missing_embeddings(
    caller: ServiceCaller, limit: int = Query(MAX_EMBEDDING_BATCH, ge=1, le=MAX_EMBEDDING_BATCH)
) -> list[TopicToEmbed]:
    """Preparation topics saved before embeddings existed, for the one-off backfill."""
    return [
        TopicToEmbed(id=topic_id, title=title, subtopics=subtopics)
        for topic_id, title, subtopics in await reuse.missing(limit)
    ]


@router.put("/embeddings", status_code=status.HTTP_204_NO_CONTENT)
async def save_embeddings(body: list[TopicEmbedding], caller: ServiceCaller) -> None:
    await reuse.save({item.id: item.embedding for item in body})
