import logging
import math

from app.config.settings import settings
from app.constants.reuse import MAX_REUSE_SHARE
from app.integrations import library, llm
from app.models.state import State
from app.schemas.library import ReuseIn

logger = logging.getLogger(__name__)


def topic_text(topic: dict) -> str:
    if not topic["subtopics"]:
        return topic["main_topic"]

    return f"{topic['main_topic']}: {', '.join(topic['subtopics'])}"


async def find_reused(state: State) -> dict:
    """Embeds the approved topics and takes proven questions from similar public topics.

    Reuse only saves cost, so any failure here means generating every question instead.
    """
    topics = state["topics"]
    count = math.floor(settings.questions_per_topic * MAX_REUSE_SHARE)

    try:
        embeddings = await llm.get_embeddings().aembed_documents(
            [topic_text(topic) for topic in topics]
        )
    except Exception:
        logger.exception("Couldn't embed the topics")

        return {"topic_embeddings": [], "reused": [[] for _ in topics]}

    reused = []

    for embedding in embeddings:
        try:
            found = (
                await library.find_reusable(
                    ReuseIn(embedding=embedding, level=state["level"], count=count)
                )
                if count
                else []
            )
        except Exception:
            logger.exception("Couldn't find questions to reuse")
            found = []

        reused.append([question.model_dump() for question in found])

    return {"topic_embeddings": embeddings, "reused": reused}
