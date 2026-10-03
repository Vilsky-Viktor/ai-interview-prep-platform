import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.reuse import MAX_TOPIC_DISTANCE, MIN_REUSE_ANSWERS
from app.constants.sets import SetKind, Visibility
from app.storage.db import Session

SAVE_EMBEDDING_SQL = text("UPDATE topics SET embedding = CAST(:embedding AS vector) WHERE id = :id")

# Preparation topics saved before embeddings existed. Private ones too: they may be made public.
MISSING_SQL = text(
    """
    SELECT t.id, t.title, t.subtopics FROM topics t JOIN sets s ON s.id = t.set_id
    WHERE s.kind = :kind AND t.embedding IS NULL
    ORDER BY t.id
    LIMIT :limit
    """
)

# Proven questions from public preparations of the level whose topic is close to the new one.
# The same text can sit in several preparations; each is offered once, from its closest topic.
FIND_SQL = text(
    """
    SELECT text, options FROM (
        SELECT DISTINCT ON (q.text) q.text, q.options, qs.answers,
            t.embedding <=> CAST(:embedding AS vector) AS distance
        FROM topics t
        JOIN sets s ON s.id = t.set_id
        JOIN questions q ON q.topic_id = t.id
        JOIN question_stats qs ON qs.question_id = q.id
        WHERE s.visibility = :visibility AND s.kind = :kind AND s.level = :level
            AND s.language = :language
            AND t.embedding <=> CAST(:embedding AS vector) <= :max_distance
            AND qs.flag IS NULL AND qs.answers >= :min_answers
        ORDER BY q.text, distance
    ) candidates
    ORDER BY distance, answers DESC
    LIMIT :count
    """
)


def as_vector(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


async def save_embeddings(
    session: AsyncSession, topic_ids: list[uuid.UUID], embeddings: list[list[float] | None]
) -> None:
    for topic_id, embedding in zip(topic_ids, embeddings):
        if embedding is not None:
            await session.execute(
                SAVE_EMBEDDING_SQL, {"id": topic_id, "embedding": as_vector(embedding)}
            )


async def find(
    embedding: list[float], level: str, language: str, count: int
) -> list[tuple[str, list]]:
    params = {
        "embedding": as_vector(embedding),
        "visibility": Visibility.PUBLIC,
        "kind": SetKind.PREPARATION,
        "level": level,
        "language": language,
        "max_distance": MAX_TOPIC_DISTANCE,
        "min_answers": MIN_REUSE_ANSWERS,
        "count": count,
    }

    async with Session() as session:
        return [tuple(row) for row in await session.execute(FIND_SQL, params)]


async def missing(limit: int) -> list[tuple[uuid.UUID, str, list[str]]]:
    async with Session() as session:
        rows = await session.execute(MISSING_SQL, {"kind": SetKind.PREPARATION, "limit": limit})

        return [tuple(row) for row in rows]


async def save(embeddings: dict[uuid.UUID, list[float]]) -> None:
    async with Session() as session:
        await save_embeddings(session, list(embeddings), list(embeddings.values()))
        await session.commit()
