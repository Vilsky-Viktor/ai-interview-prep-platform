import logging
from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI, HTTPException, status
from prepza_common import http
from prepza_common.i18n import add_localized_errors
from prepza_common.logging import RequestLogMiddleware, configure_logging
from prepza_common.sentry import init_sentry

from app.config.settings import settings
from app.routers import auto_top_ups, billing, internal, superadmin
from app.storage.db import ping as ping_database

configure_logging()
init_sentry("billing")


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})

    yield

    await http.get_client().aclose()


app = FastAPI(
    title="billing",
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.api_docs else None,
)
add_localized_errors(app)
app.add_middleware(RequestLogMiddleware)
app.include_router(billing.router)
app.include_router(internal.router)
app.include_router(auto_top_ups.internal)
app.include_router(superadmin.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict:
    """Ready only once the database answers; Docker's healthcheck uses this."""
    try:
        await ping_database()
    except Exception:
        logging.getLogger(__name__).exception("Not ready")
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Not ready")

    return {"status": "ready"}
