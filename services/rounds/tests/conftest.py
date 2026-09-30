import os

os.environ.setdefault("FIREBASE_PROJECT_ID", "demo-test")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("LIBRARY_URL", "http://library")
os.environ.setdefault("REDIS_URL", "redis://localhost")
os.environ.setdefault("SERVICE_SECRET", "test-secret-that-is-at-least-32-bytes")
os.environ.setdefault("LLM_LIMIT", "0")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
