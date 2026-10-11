import logging
from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI, HTTPException, status
from prepza_common import http
from prepza_common.body_limit import BodyLimitMiddleware
from prepza_common.i18n import add_localized_errors
from prepza_common.logging import RequestLogMiddleware, configure_logging
from prepza_common.maintenance import MaintenanceMiddleware
from prepza_common.sentry import init_sentry

from app.config.settings import settings
from app.constants.docs import API_DESCRIPTION, API_TITLE, API_VERSION
from app.constants.events import CANDIDATE_FINISHED
from app.integrations import webhooks as endpoints
from app.integrations.redis import get_redis
from app.routers import events, internal_accounts, manage, public, schedules
from app.schemas.public import FinishedEvent
from app.storage.db import ping as ping_database

configure_logging()
# httpx logs every request's full URL at INFO; a web hook's URL can carry a secret in its path.
logging.getLogger("httpx").setLevel(logging.WARNING)
init_sentry("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})

    yield

    await http.get_client().aclose()
    await endpoints.get_client().aclose()
    await get_redis().aclose()


# The reference lists the public routes only; the site's API page shows it.
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    servers=[{"url": f"{settings.site_url}/api/v1"}],
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)
add_localized_errors(app)
app.add_middleware(MaintenanceMiddleware, get_redis=get_redis)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(BodyLimitMiddleware)
app.include_router(public.router)
app.include_router(manage.router)
app.include_router(events.router)
app.include_router(internal_accounts.router)
app.include_router(schedules.router)


@app.webhooks.post(CANDIDATE_FINISHED, summary="A candidate finished")
def candidate_finished(event: FinishedEvent) -> None:
    """Sent when a candidate finishes one of your interviews. The request body is a JSON object
    with the event's `id`, its `type` (`candidate.finished`) and `data`, described below."""


@app.get("/health", include_in_schema=False)
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready", include_in_schema=False)
async def ready() -> dict:
    """Ready once the database answers; Docker's healthcheck and the startup probe use this. Redis
    isn't checked: an outage there shouldn't stop the service from starting."""
    try:
        await ping_database()
    except Exception:
        logging.getLogger(__name__).exception("Not ready")
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Not ready")

    return {"status": "ready"}
