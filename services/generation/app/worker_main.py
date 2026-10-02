import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from prepza_common import http
from prepza_common.logging import RequestLogMiddleware, configure_logging
from prepza_common.sentry import init_sentry

from app.integrations.redis import get_redis
from app.routers import jobs, schedules
from app.services.graph import build_graph
from app.storage.checkpointer import open_checkpointer
from app.storage.db import ping as ping_database

configure_logging()
init_sentry("generation-worker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """The worker: Cloud Tasks runs jobs and Cloud Scheduler runs schedules through it."""
    app.state.pool, app.state.checkpointer = await open_checkpointer()
    app.state.graph = build_graph(app.state.checkpointer)

    yield

    await app.state.pool.close()
    await get_redis().aclose()
    await http.get_client().aclose()


# Only Google calls it, so there's no API description to serve.
app = FastAPI(title="generation-worker", lifespan=lifespan, openapi_url=None)
app.add_middleware(RequestLogMiddleware)
app.include_router(jobs.router)
app.include_router(schedules.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict:
    try:
        await ping_database()
    except Exception:
        logging.getLogger(__name__).exception("Not ready")

        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Not ready")

    return {"status": "ready"}
