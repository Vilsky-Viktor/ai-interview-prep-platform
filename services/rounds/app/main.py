import logging
import os
from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI, HTTPException, status
from prepza_common import http
from prepza_common.logging import RequestLogMiddleware, configure_logging

from app.config.settings import settings
from app.integrations.redis import get_redis
from app.routers import (
    certificates,
    chat,
    internal,
    preparations,
    rounds,
    session_feedback,
    sessions,
    topics,
)
from app.storage.db import ping as ping_database

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})

    if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
        logger.info("LangSmith tracing enabled")

    yield

    await get_redis().aclose()
    await http.get_client().aclose()


app = FastAPI(title="rounds", lifespan=lifespan)
app.add_middleware(RequestLogMiddleware)
app.include_router(rounds.router)
app.include_router(sessions.router)
app.include_router(session_feedback.router)
app.include_router(topics.router)
app.include_router(preparations.router)
app.include_router(chat.router)
app.include_router(certificates.router)
app.include_router(internal.router)


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
