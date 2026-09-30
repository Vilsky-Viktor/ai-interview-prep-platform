import logging
import os
import uuid

from arq.connections import RedisSettings

from app.config.settings import settings
from app.constants.generation import GENERATION_FAILED, JOB_TIMEOUT_SECONDS, MAX_WORKER_JOBS
from app.constants.statuses import Status
from app.helpers.logging import configure_logging
from app.services.graph import build_graph
from app.services.pipeline import run_pipeline
from app.storage import generations
from app.storage.checkpointer import open_checkpointer

logger = logging.getLogger(__name__)


async def run_generation(ctx: dict, generation_id: str, resume: dict | None = None) -> None:
    generation = await generations.get(uuid.UUID(generation_id))

    if generation is None:
        return

    try:
        await run_pipeline(ctx["graph"], generation, resume)
    except Exception:
        logger.exception("Generation %s failed", generation_id)
        await generations.update(generation.id, status=Status.FAILED, error=GENERATION_FAILED)


async def startup(ctx: dict) -> None:
    configure_logging()

    if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
        logger.info("LangSmith tracing enabled")

    ctx["pool"], checkpointer = await open_checkpointer()
    ctx["graph"] = build_graph(checkpointer)


async def shutdown(ctx: dict) -> None:
    await ctx["pool"].close()


class WorkerSettings:
    functions = [run_generation]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    job_timeout = JOB_TIMEOUT_SECONDS
    max_jobs = MAX_WORKER_JOBS
