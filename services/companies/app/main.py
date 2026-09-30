from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI

from app.config.settings import settings
from app.helpers.logging import RequestLogMiddleware, configure_logging
from app.integrations.events import get_redis
from app.routers import (
    companies,
    interview_generation,
    interview_questions,
    interviews,
    invites,
    members,
)

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})

    yield

    await get_redis().aclose()


app = FastAPI(title="companies", lifespan=lifespan)
app.add_middleware(RequestLogMiddleware)
app.include_router(companies.router)
app.include_router(members.router)
app.include_router(interviews.router)
app.include_router(interview_generation.router)
app.include_router(interview_questions.router)
app.include_router(invites.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
