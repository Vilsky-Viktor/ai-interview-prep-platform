import asyncio
import logging
import uuid

from prepza_common.analytics import track

from app.constants.generation import GENERATION_FAILED, GENERATION_STOPPED, JOB_TIMEOUT_SECONDS
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status
from app.integrations import billing
from app.services.pipeline import run_pipeline
from app.storage import generations

logger = logging.getLogger(__name__)


async def run_generation(graph, generation_id: uuid.UUID, resume: dict | None) -> None:
    """Runs one generation to its end or its review. Never raises: a failure is saved on the
    generation, which the user can retry, so Cloud Tasks never runs it twice."""
    generation = await generations.get(generation_id)

    # Cancelled while it waited, or failed by the sweeper before it started.
    if generation is None:
        return

    if generation.status in (Status.CANCELLED, Status.FAILED):
        await give_back(generation, generation.status)

        return

    try:
        await asyncio.wait_for(run_pipeline(graph, generation, resume), JOB_TIMEOUT_SECONDS)
    except TimeoutError:
        logger.error("Generation %s ran out of time", generation_id)
        await generations.update(generation.id, status=Status.FAILED, error=GENERATION_STOPPED)
        await give_back(generation, "timeout")
    except Exception:
        logger.exception("Generation %s failed", generation_id)
        await generations.update(generation.id, status=Status.FAILED, error=GENERATION_FAILED)
        await give_back(generation, "error")


async def give_back(generation, why: str) -> None:
    """A learner's kit that didn't finish costs nothing. Interviews aren't charged."""
    if generation.kind == GenerationKind.PREPARATION:
        await billing.release_kit(generation.id)
        await track("kit_failed", user_id=generation.owner_uid, why=why)
