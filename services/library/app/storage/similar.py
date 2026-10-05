import uuid

from sqlalchemy import text

from app.constants.sets import SetKind
from app.constants.talents import MIN_SHARED_TOPICS, SIMILAR_TOPIC_DISTANCE
from app.storage.db import Session

# The templates for roles like a company's test: the ones its questions were copied from first,
# then those that cover most of its topics and that it covers most of, by meaning (MIN_SHARED_TOPICS
# both ways), best covered first.
SIMILAR_SQL = text(
    """
    WITH copied AS (
        SELECT DISTINCT tt.set_id AS template_id
        FROM topics ct
        JOIN questions cq ON cq.topic_id = ct.id
        JOIN questions sq ON sq.id = cq.source_question_id
        JOIN topics tt ON tt.id = sq.topic_id
        WHERE ct.set_id = :set_id
    ),
    test_topics AS (
        SELECT id, embedding FROM topics WHERE set_id = :set_id AND embedding IS NOT NULL
    ),
    alike AS (
        SELECT ts.id AS template_id, ts.topic_count, ct.id AS test_topic, tt.id AS template_topic
        FROM test_topics ct
        JOIN topics tt ON tt.embedding <=> ct.embedding <= :max_distance
        JOIN sets ts ON ts.id = tt.set_id AND ts.kind = :kind
    ),
    covered AS (
        SELECT template_id,
            count(DISTINCT test_topic)::float / (SELECT count(*) FROM test_topics) AS test_share,
            count(DISTINCT template_topic)::float / max(topic_count) AS template_share
        FROM alike
        GROUP BY template_id
    )
    SELECT template_id FROM (
        SELECT template_id, 2.0 AS rank FROM copied
        UNION ALL
        SELECT template_id, least(test_share, template_share) AS rank
        FROM covered
        WHERE test_share >= :min_share AND template_share >= :min_share
            AND template_id NOT IN (SELECT template_id FROM copied)
    ) found
    ORDER BY rank DESC
    LIMIT :limit
    """
)


async def similar_templates(set_id: uuid.UUID, limit: int) -> list[uuid.UUID]:
    params = {
        "set_id": set_id,
        "max_distance": SIMILAR_TOPIC_DISTANCE,
        "min_share": MIN_SHARED_TOPICS,
        "kind": SetKind.TEMPLATE,
        "limit": limit,
    }

    async with Session() as session:
        return [row.template_id for row in await session.execute(SIMILAR_SQL, params)]
