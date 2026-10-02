from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prepza_common.service_auth import issue_token, service_caller

SECRET = "test-secret-that-is-at-least-32-bytes"
OTHER_SECRET = "another-secret-that-is-at-least-32-b"


def client():
    app = FastAPI()
    caller = service_caller(SECRET)

    @app.get("/internal")
    def internal(name: caller) -> dict:
        return {"caller": name}

    return TestClient(app)


def call(token):
    return client().get("/internal", headers={"Authorization": f"Bearer {token}"})


def test_a_token_signed_with_the_secret_names_its_service():
    response = call(issue_token("companies", SECRET))

    assert response.status_code == 200
    assert response.json() == {"caller": "companies"}


@pytest.mark.parametrize(
    "token",
    [
        issue_token("companies", OTHER_SECRET),
        jwt.encode(
            {"iss": "companies", "exp": datetime.now(UTC) - timedelta(seconds=1)},
            SECRET,
            algorithm="HS256",
        ),
        jwt.encode({"iss": "companies"}, SECRET, algorithm="HS256"),
    ],
    ids=["wrong secret", "expired", "no expiry"],
)
def test_other_tokens_are_refused(token):
    assert call(token).status_code == 401
