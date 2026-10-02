import logging
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import ClassVar

from arq import cron
from arq.connections import RedisSettings
from prepza_common import http
from prepza_common.logging import configure_logging

from app.config.settings import settings
from app.constants.events import GENERATION_CANCELLED
from app.constants.generation import (
    GENERATION_FAILED,
    GENERATION_STOPPED,
    JOB_TIMEOUT_SECONDS,
    MAX_WORKER_JOBS,
    REVIEW_EXPIRY_DAYS,
    STUCK_AFTER_SECONDS,
    SWEEP_MINUTES,
)
from app.constants.kinds import GenerationKind
from app.constants.quality import KEY_CHECK_MINUTES, QualityFlag
from app.constants.statuses import Status
from app.integrations import events
from app.services.graph import build_graph
from app.services.key_check_batches import collect_finished, submit_pending
from app.services.pipeline import run_pipeline
from app.services.verify import verify
from app.storage import generations
from app.storage.checkpointer import open_checkpointer

logger = logging.getLogger(__name__)


async def run_generation(ctx: dict, generation_id: str, resume: dict | None = None) -> None:
    generation = await generations.get(uuid.UUID(generation_id))

    # Cancelled while it waited in the queue, or failed by the sweeper before it started.
    if generation is None or generation.status in (Status.CANCELLED, Status.FAILED):
        return

    try:
        await run_pipeline(ctx["graph"], generation, resume)
    except Exception:
        logger.exception("Generation %s failed", generation_id)
        await generations.update(generation.id, status=Status.FAILED, error=GENERATION_FAILED)


async def verify_question(ctx: dict, question_id: str, flag: str) -> None:
    await verify(uuid.UUID(question_id), QualityFlag(flag))


async def key_check_batches(ctx: dict) -> None:
    """Applies finished OpenAI batches of key checks, then sends the waiting ones."""
    await collect_finished()
    await submit_pending()


async def expire_reviews() -> None:
    """Cancels topic reviews left open for REVIEW_EXPIRY_DAYS; an interview is removed with it."""
    before = datetime.now(UTC) - timedelta(days=REVIEW_EXPIRY_DAYS)

    for generation in await generations.expire_reviews(before):
        if generation.kind == GenerationKind.INTERVIEW:
            await events.publish(GENERATION_CANCELLED, {"generation_id": str(generation.id)})


async def sweep(ctx: dict) -> None:
    """Fails generations whose worker died mid-job, so the user can Retry them, and deletes
    checkpoints nothing will resume. Failed and in-review generations keep theirs."""
    before = datetime.now(UTC) - timedelta(seconds=STUCK_AFTER_SECONDS)
    count = await generations.fail_stuck(before, GENERATION_STOPPED)

    if count:
        logger.warning("Marked %d stuck generations as failed", count)

    await expire_reviews()

    for thread_id in await generations.finished_threads():
        await ctx["checkpointer"].adelete_thread(thread_id)


async def startup(ctx: dict) -> None:
    configure_logging()

    if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
        logger.info("LangSmith tracing enabled")

    ctx["pool"], ctx["checkpointer"] = await open_checkpointer()
    ctx["graph"] = build_graph(ctx["checkpointer"])


async def shutdown(ctx: dict) -> None:
    await ctx["pool"].close()
    await events.get_redis().aclose()
    await http.get_client().aclose()


class WorkerSettings:
    functions: ClassVar = [run_generation, verify_question]
    cron_jobs: ClassVar = [
        cron(sweep, minute=SWEEP_MINUTES),
        cron(key_check_batches, minute=KEY_CHECK_MINUTES),
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    job_timeout = JOB_TIMEOUT_SECONDS
    max_jobs = MAX_WORKER_JOBS
