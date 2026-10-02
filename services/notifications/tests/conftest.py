import os

os.environ.setdefault("SMTP_HOST", "localhost")
os.environ.setdefault("SITE_URL", "http://localhost:8090")
# A demo- project: no Google Cloud, so calls from Pub/Sub, Cloud Tasks and Scheduler aren't
# token-checked, and jobs run locally.
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "demo-test")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
