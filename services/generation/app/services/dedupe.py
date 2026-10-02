import logging
import operator

from app.constants.generation import DUPLICATE_DISTANCE
from app.integrations import llm

logger = logging.getLogger(__name__)


async def distinct_by_meaning(texts: list[str], keep_first: int = 0) -> list[int]:
    """Indexes of the texts to keep, dropping any that ask what an earlier kept one asks.

    The first `keep_first` texts are always kept. Without embeddings, every text is kept.
    """
    try:
        vectors = await llm.get_embeddings().aembed_documents(texts)
    except Exception:
        logger.exception("Couldn't embed questions to drop duplicates")

        return list(range(len(texts)))

    kept = list(range(min(keep_first, len(texts))))

    for index in range(len(kept), len(texts)):
        # OpenAI embeddings have length 1, so the dot product is the cosine similarity.
        if all(
            1 - sum(map(operator.mul, vectors[index], vectors[other])) > DUPLICATE_DISTANCE
            for other in kept
        ):
            kept.append(index)

    return kept
