import asyncio
import uuid

from app.integrations import greenhouse
from app.models.ats import AtsConnection
from app.services import ats as integrations


def test_a_client_gets_only_its_own_credentials_not_the_web_hooks_secret(monkeypatch):
    connection = AtsConnection(id=uuid.uuid4(), provider="greenhouse", status="connected")
    asked = []

    async def credentials(found):
        return {"client_id": "id", "client_secret": "secret", "webhook_secret": "hook"}

    async def listed(client_id, client_secret, path, params):
        asked.append((client_id, client_secret, path))

        return [{"id": 7, "name": "Accountant"}]

    monkeypatch.setattr(integrations, "credentials", credentials)
    monkeypatch.setattr(greenhouse, "_list", listed)

    assert asyncio.run(integrations.jobs(connection)) == [{"id": "7", "name": "Accountant"}]
    assert asked == [("id", "secret", "/jobs")]
