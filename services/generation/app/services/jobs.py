import asyncio
import logging
import uuid

from app.constants.generation import GENERATION_FAILED, GENERATION_STOPPED, JOB_TIMEOUT_SECONDS
from app.constants.statuses import Status
from app.services.pipeline import run_pipeline
from app.storage import generations

logger = logging.getLogger(__name__)


async def run_generation(graph, generation_id: uuid.UUID, resume: dict | None) -> None:
    """Runs one generation to its end or its review. Never raises: a failure is saved on the
    generation, which the user can retry, so Cloud Tasks never runs it twice."""
    generation = await generations.get(generation_id)

    # Cancelled while it waited, or failed by the sweeper before it started.
    if generation is None or generation.status in (Status.CANCELLED, Status.FAILED):
        return

    try:
        await asyncio.wait_for(run_pipeline(graph, generation, resume), JOB_TIMEOUT_SECONDS)
    except TimeoutError:
        logger.error("Generation %s ran out of time", generation_id)
        await generations.update(generation.id, status=Status.FAILED, error=GENERATION_STOPPED)
    except Exception:
        logger.exception("Generation %s failed", generation_id)
        await generations.update(generation.id, status=Status.FAILED, error=GENERATION_FAILED)
