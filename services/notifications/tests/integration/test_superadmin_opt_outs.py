import json
import uuid

import httpx
import pytest
from prepza_common import http
from prepza_common.auth import current_user
from prepza_common.user import User
from sqlalchemy import func, select

from app.config.settings import settings
from app.helpers.unsubscribe import address_hash
from app.main import app
from app.models.opt_outs import CandidateOptOut
from app.storage import opt_outs
from app.storage.db import Session
from tests.integration.factories import api


@pytest.fixture
def acme(monkeypatch):
    """Companies at the HTTP boundary: Acme invited the address; the superadmin Sam signs in."""
    company = f"c-{uuid.uuid4()}"
    monkeypatch.setenv("SUPERADMIN_EMAILS", "sam@prepza.dev")
    monkeypatch.setattr(settings, "companies_url", "http://companies")

    def answer(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/internal/invites/companies":
            return httpx.Response(200, json={"company_ids": [company]})

        ids = json.loads(request.content)["company_ids"]

        return httpx.Response(
            200, json={"companies": [{"id": id, "name": "Acme", "members": []} for id in ids]}
        )

    monkeypatch.setattr(
        http, "get_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(answer))
    )
    app.dependency_overrides[current_user] = lambda: User(
        uid="sam", email="sam@prepza.dev", email_verified=True
    )
    yield company

    app.dependency_overrides.clear()


def test_stopping_twice_stores_one_opt_out_and_letting_through_removes_reminders_too(run, acme):
    email = f"dee-{uuid.uuid4()}@example.com"
    address = address_hash(email)

    async def count():
        async with Session() as session:
            return await session.scalar(
                select(func.count()).where(
                    CandidateOptOut.address == address, CandidateOptOut.company_id == acme
                )
            )

    async def scenario():
        # One invite's reminders, stopped from an email's link.
        await opt_outs.add(address, acme, "invite-1")

        async with api() as client:
            body = {"email": email.upper(), "company_id": acme, "stopped": True}
            stops = [(await client.put("/superadmin/candidate-opt-outs", json=body)).json()]
            stops.append((await client.put("/superadmin/candidate-opt-outs", json=body)).json())
            stored = await count()
            body["stopped"] = False

            for _ in range(2):
                through = await client.put("/superadmin/candidate-opt-outs", json=body)

            looked = await client.post(
                "/superadmin/candidate-opt-outs/lookup", json={"email": email}
            )

        return stops, stored, through.json(), looked.json(), await count()

    stops, stored, through, looked, left = run(scenario())

    stopped = {"company_id": acme, "name": "Acme", "stopped": True, "stopped_reminders": 1}
    assert stops == [{"companies": [stopped]}, {"companies": [stopped]}]
    assert stored == 2
    cleared = {**stopped, "stopped": False, "stopped_reminders": 0}
    assert through == looked == {"companies": [cleared]}
    assert left == 0
