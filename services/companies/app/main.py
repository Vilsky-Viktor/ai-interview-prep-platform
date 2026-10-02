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
    companies,
    internal_accounts,
    internal_events,
    internal_invites,
    interview_generation,
    interview_questions,
    interviews,
    invites,
    members,
    schedules,
)
from app.storage.db import ping as ping_database

configure_logging()
init_sentry("companies")


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})
    yield

    await get_redis().aclose()
    await http.get_client().aclose()


app = FastAPI(
    title="companies",
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.api_docs else None,
)
app.add_middleware(RequestLogMiddleware)
app.include_router(companies.router)
app.include_router(members.router)
app.include_router(interviews.router)
app.include_router(interview_generation.router)
app.include_router(interview_questions.router)
app.include_router(invites.router)
app.include_router(internal_accounts.router)
app.include_router(internal_invites.router)
app.include_router(internal_events.router)
app.include_router(schedules.router)


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
