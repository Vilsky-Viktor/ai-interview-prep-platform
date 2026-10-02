def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def fake_services(monkeypatch, database_up=True):
    from app import main

    async def ping_database():
        if not database_up:
            raise ConnectionError("database is down")

    class FakeRedis:
        async def ping(self):
            return True

    monkeypatch.setattr(main, "get_redis", FakeRedis)
    monkeypatch.setattr(main, "ping_database", ping_database)


def test_ready_when_database_and_redis_answer(client, monkeypatch):
    fake_services(monkeypatch)

    assert client.get("/ready").json() == {"status": "ready"}


def test_not_ready_while_the_database_is_down(client, monkeypatch):
    fake_services(monkeypatch, database_up=False)

    assert client.get("/ready").status_code == 503
