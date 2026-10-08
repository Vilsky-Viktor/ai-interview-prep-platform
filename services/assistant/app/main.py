import logging
from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI, HTTPException, status
from prepza_common import http
from prepza_common.i18n import add_localized_errors
from prepza_common.logging import RequestLogMiddleware, configure_logging
from prepza_common.maintenance import MaintenanceMiddleware
from prepza_common.sentry import init_sentry

from app.config.settings import settings
from app.integrations.redis import get_redis
from app.routers import (
    chat,
    conversations,
    events,
    internal_accounts,
    schedules,
    transcribe,
)
from app.services.registry import tools
from app.storage.db import ping as ping_database

configure_logging()
# httpx logs every request's full URL at INFO; a tool's query can hold what the user searched for.
logging.getLogger("httpx").setLevel(logging.WARNING)
init_sentry("assistant")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Every tool is built now: one whose route left its service's snapshot stops the start.
    tools()
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})

    yield

    await http.get_client().aclose()
    await get_redis().aclose()


app = FastAPI(
    title="assistant",
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.api_docs else None,
)
add_localized_errors(app)
app.add_middleware(MaintenanceMiddleware, get_redis=get_redis)
app.add_middleware(RequestLogMiddleware)
app.include_router(chat.router)
app.include_router(transcribe.router)
app.include_router(conversations.router)
app.include_router(events.router)
app.include_router(schedules.router)
app.include_router(internal_accounts.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict:
    """Ready once the database answers; Docker's healthcheck and the startup probe use this. Redis
    isn't checked: an outage there shouldn't stop the service from starting."""
    try:
        await ping_database()
    except Exception:
        logging.getLogger(__name__).exception("Not ready")
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Not ready")

    return {"status": "ready"}
