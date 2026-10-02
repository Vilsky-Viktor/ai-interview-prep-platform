import asyncio
import uuid

from sqlalchemy.dialects import postgresql

from app.service_auth import service_token
from app.storage import rounds, sessions

PREPARATION_ID = uuid.uuid4()


def fake_session(monkeypatch, statements):
    class Result:
        rowcount = 1

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def execute(self, statement):
            statements.append(statement)

            return Result()

        async def scalars(self, statement):
            return []

        async def commit(self):
            pass

    monkeypatch.setattr(rounds, "Session", FakeSession)


def compiled(statement) -> str:
    return str(statement.compile(dialect=postgresql.dialect()))


def test_library_deletes_a_preparations_practice_data(client, monkeypatch):
    removed = []

    async def fake_remove(preparation_id):
        removed.append(preparation_id)

    monkeypatch.setattr(rounds, "remove_for_preparation", fake_remove)
    url = f"/internal/preparations/{PREPARATION_ID}"

    response = client.delete(url, headers={"Authorization": f"Bearer {service_token('rounds')}"})

    assert response.status_code == 204
    assert removed == [PREPARATION_ID]


def test_cleanup_needs_a_service_token(client):
    for url in (
        f"/internal/preparations/{PREPARATION_ID}",
        f"/internal/interviews/{PREPARATION_ID}",
    ):
        assert client.delete(url).status_code in (401, 403)


def test_companies_deletes_an_interviews_sessions(client, monkeypatch):
    removed = []

    async def fake_remove(interview_set_id):
        removed.append(interview_set_id)

    monkeypatch.setattr(sessions, "remove_for_interview", fake_remove)
    url = f"/internal/interviews/{PREPARATION_ID}"

    response = client.delete(url, headers={"Authorization": f"Bearer {service_token('rounds')}"})

    assert response.status_code == 204
    assert removed == [PREPARATION_ID]


def test_preparation_cleanup_keeps_certificates(monkeypatch):
    statements = []
    fake_session(monkeypatch, statements)

    asyncio.run(rounds.remove_for_preparation(PREPARATION_ID))

    sql = [compiled(statement) for statement in statements]
    assert any(line.startswith("DELETE FROM question_progress") for line in sql)
    assert any(line.startswith("DELETE FROM rounds") for line in sql)
    assert not any("certificates" in line for line in sql)


def test_deleting_one_round_still_removes_its_certificate(monkeypatch):
    statements = []
    fake_session(monkeypatch, statements)

    asyncio.run(rounds.remove(uuid.uuid4(), "user-1"))

    sql = [compiled(statement) for statement in statements]
    assert sql[0].startswith("DELETE FROM certificates")
    assert sql[1].startswith("DELETE FROM rounds")
