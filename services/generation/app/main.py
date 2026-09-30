from contextlib import asynccontextmanager

import firebase_admin
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from app.config.settings import settings
from app.helpers.logging import RequestLogMiddleware, configure_logging
from app.routers import generations, internal, questions

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})
    app.state.arq = await create_pool(RedisSettings.from_dsn(settings.redis_url))

    yield

    await app.state.arq.aclose()


app = FastAPI(title="generation", lifespan=lifespan)
app.add_middleware(RequestLogMiddleware)
app.include_router(generations.router)
app.include_router(questions.router)
app.include_router(internal.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
