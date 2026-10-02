import logging
from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI, HTTPException, status
from prepza_common import http
from prepza_common.logging import RequestLogMiddleware, configure_logging
from prepza_common.sentry import init_sentry

from app.config.settings import settings
from app.integrations.redis import get_redis
from app.routers import (
    internal,
    internal_events,
    internal_feedback,
    internal_quality,
    internal_reuse,
    internal_shares,
    joins,
    library,
    me,
    preparations,
    questions,
    schedules,
    shares,
)
from app.storage.db import ping as ping_database

configure_logging()
init_sentry("library")


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})
    yield

    await get_redis().aclose()
    await http.get_client().aclose()


app = FastAPI(
    title="library",
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.api_docs else None,
)
app.add_middleware(RequestLogMiddleware)
app.include_router(me.router)
app.include_router(preparations.router)
app.include_router(joins.router)
app.include_router(shares.router)
app.include_router(questions.router)
app.include_router(library.router)
app.include_router(internal.router)
app.include_router(schedules.router)
app.include_router(internal_events.router)
app.include_router(internal_feedback.router)
app.include_router(internal_quality.router)
app.include_router(internal_reuse.router)
app.include_router(internal_shares.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict:
    """Ready only once the database and Redis answer; Docker's healthcheck uses this."""
    try:
        await ping_database()
        await get_redis().ping()
    except Exception:
        logging.getLogger(__name__).exception("Not ready")

        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Not ready")

    return {"status": "ready"}
