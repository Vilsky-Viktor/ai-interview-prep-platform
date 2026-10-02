from contextlib import asynccontextmanager

from fastapi import FastAPI
from prepza_common import http
from prepza_common.logging import RequestLogMiddleware, configure_logging
from prepza_common.sentry import init_sentry

from app.routers import events

configure_logging()
init_sentry("notifications")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await http.get_client().aclose()


# Only Pub/Sub calls it, so there's no API description to serve.
app = FastAPI(title="notifications", lifespan=lifespan, openapi_url=None)
app.add_middleware(RequestLogMiddleware)
app.include_router(events.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    """Nothing to check: it holds no connections of its own."""
    return {"status": "ready"}
