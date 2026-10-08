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
    accommodations,
    audit,
    auto_top_ups,
    bulk_invites,
    candidates,
    companies,
    internal_accounts,
    internal_api,
    internal_ats,
    internal_events,
    internal_invites,
    internal_reminders,
    interview_generation,
    interview_questions,
    interviews,
    invites,
    links,
    logos,
    maintenance,
    members,
    pause,
    reports,
    schedules,
    superadmin,
    superadmin_verification,
    verification,
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
add_localized_errors(app)
app.add_middleware(MaintenanceMiddleware, get_redis=get_redis)
app.add_middleware(RequestLogMiddleware)
app.include_router(companies.router)
app.include_router(audit.router)
app.include_router(auto_top_ups.router)
app.include_router(members.router)
app.include_router(interviews.router)
app.include_router(candidates.router)
app.include_router(accommodations.router)
app.include_router(bulk_invites.router)
app.include_router(interview_generation.router)
app.include_router(interview_questions.router)
app.include_router(invites.router)
app.include_router(links.router)
app.include_router(logos.router)
app.include_router(reports.router)
app.include_router(verification.router)
app.include_router(internal_accounts.router)
app.include_router(internal_ats.router)
app.include_router(internal_api.router)
app.include_router(internal_invites.router)
app.include_router(internal_reminders.router)
app.include_router(internal_events.router)
app.include_router(schedules.router)
app.include_router(pause.router)
app.include_router(maintenance.router)
app.include_router(superadmin.router)
app.include_router(superadmin_verification.router)


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
