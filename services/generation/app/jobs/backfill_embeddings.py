"""Embeds preparation topics saved before reuse existed, so their questions can be reused.

Run once, from the repo root:
    docker-compose exec generation uv run --no-sync python -m app.jobs.backfill_embeddings
"""

import asyncio
import logging

from prepza_common.logging import configure_logging

from app.constants.reuse import EMBEDDING_BATCH_SIZE
from app.integrations import library, llm
from app.services.nodes.reuse import topic_text

logger = logging.getLogger(__name__)


async def backfill() -> int:
    """Embeds batch after batch until no topic is missing one; returns how many it embedded."""
    done = 0

    while topics := await library.missing_embeddings(EMBEDDING_BATCH_SIZE):
        embeddings = await llm.get_embeddings().aembed_documents(
            [topic_text({"main_topic": t["title"], "subtopics": t["subtopics"]}) for t in topics]
        )
        await library.save_embeddings(
            {topic["id"]: embedding for topic, embedding in zip(topics, embeddings)}
        )
        done += len(topics)
        logger.info("Embedded %d topics", done)

    return done


if __name__ == "__main__":
    configure_logging()
    print(f"Embedded {asyncio.run(backfill())} topics")
