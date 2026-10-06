import logging
import math

from prepza_common.constants import DEFAULT_LANGUAGE

from app.constants.reuse import MAX_REUSE_SHARE
from app.helpers.questions import topic_size
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
    share = MAX_REUSE_SHARE
    count = math.floor(topic_size(state.get("template", False)) * share)

    try:
        embeddings = await llm.get_embeddings().aembed_documents(
            [topic_text(topic) for topic in topics]
        )
    except Exception:
        logger.exception("Couldn't embed the topics")

        return {"topic_embeddings": [], "reused": [[] for _ in topics]}

    reused = []
    # A bank question goes into one topic of a test at most, even when two topics are alike; the
    # same text can sit in several templates, so it's told by its text.
    taken = set()

    for embedding in embeddings:
        try:
            found = (
                await library.find_reusable(
                    ReuseIn(
                        embedding=embedding,
                        level=state["level"],
                        language=state.get("language") or DEFAULT_LANGUAGE,
                        count=count,
                    )
                )
                if count
                else []
            )
        except Exception:
            logger.exception("Couldn't find questions to reuse")
            found = []

        found = [question for question in found if question.text not in taken]
        taken.update(question.text for question in found)
        reused.append([question.model_dump(mode="json") for question in found])

    return {"topic_embeddings": embeddings, "reused": reused}
