import uuid

from app.main import app
from app.models.generation import Generation
from app.routers import internal
from app.service_auth import service_token
from app.storage import generations

COMPANY_ID = uuid.uuid4()
GENERATION_ID = uuid.uuid4()


def headers():
    return {"Authorization": f"Bearer {service_token()}"}


def company_generation():
    return Generation(
        id=GENERATION_ID,
        owner_uid="alice",
        kind="interview",
        company_id=COMPANY_ID,
        text="Job description",
        status="awaiting_review",
        topics=[{"main_topic": "Python", "subtopics": ["asyncio"]}],
        progress=None,
        preparation_id=None,
        error=None,
    )


def fake_get(monkeypatch):
    async def get(_generation_id):
        return company_generation()

    monkeypatch.setattr(generations, "get", get)


def test_company_generation_is_visible_to_its_company(client, monkeypatch):
    fake_get(monkeypatch)
    response = client.get(
        f"/internal/generations/{GENERATION_ID}",
        params={"company_id": str(COMPANY_ID)},
        headers=headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "awaiting_review"


def test_company_generation_is_hidden_from_another_company(client, monkeypatch):
    fake_get(monkeypatch)
    response = client.get(
        f"/internal/generations/{GENERATION_ID}",
        params={"company_id": str(uuid.uuid4())},
        headers=headers(),
    )

    assert response.status_code == 404


def test_internal_generation_needs_a_service_token(client):
    response = client.get(
        f"/internal/generations/{GENERATION_ID}", params={"company_id": str(COMPANY_ID)}
    )

    assert response.status_code in (401, 403)


def test_company_review_queues_the_topics(client, monkeypatch):
    fake_get(monkeypatch)
    reviewed = []

    async def fake_submit(_arq, generation, body):
        reviewed.append(body.selected)
        generation.status = "queued"

        return generation

    monkeypatch.setattr(internal, "submit_review", fake_submit)
    monkeypatch.setattr(app.state, "arq", object(), raising=False)
    response = client.post(
        f"/internal/generations/{GENERATION_ID}/review",
        params={"company_id": str(COMPANY_ID)},
        json={"selected": [0], "instructions": ""},
        headers=headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    assert reviewed == [[0]]


def test_only_a_failed_generation_is_retried(client, monkeypatch):
    fake_get(monkeypatch)
    queued = []
    claims = iter([True, False])

    class FakeArq:
        async def enqueue_job(self, name, generation_id):
            queued.append(generation_id)

    async def fake_claim(_generation_id):
        return next(claims)

    monkeypatch.setattr(generations, "claim_retry", fake_claim)
    monkeypatch.setattr(app.state, "arq", FakeArq(), raising=False)
    url = f"/internal/generations/{GENERATION_ID}/retry"
    params = {"company_id": str(COMPANY_ID)}

    assert client.post(url, params=params, headers=headers()).status_code == 200
    assert client.post(url, params=params, headers=headers()).status_code == 409
    assert queued == [str(GENERATION_ID)]
