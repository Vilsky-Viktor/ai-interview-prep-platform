def test_visitors_send_contact_messages(client, monkeypatch):
    saved = []

    async def fake_save(data):
        saved.append(data)

    async def fake_flush():
        return None

    monkeypatch.setattr("app.routers.help.contact_store.save", fake_save)
    monkeypatch.setattr("app.routers.help.outbox_service.flush_quietly", fake_flush)
    body = {"name": " Ann ", "email": "ann@example.com", "message": "Do you offer invoices?"}

    response = client.post("/help/contact", json=body, headers={"Accept-Language": "de"})

    assert response.status_code == 204
    assert saved == [
        {
            "name": "Ann",
            "email": "ann@example.com",
            "message": "Do you offer invoices?",
            "language": "de",
        }
    ]


def test_contact_messages_are_limited_per_address_and_in_all(client, monkeypatch):
    keys = []

    async def record(redis, key, limit, window):
        keys.append(key)

    async def fake_save(data):
        return None

    async def fake_flush():
        return None

    monkeypatch.setattr("app.routers.help.hit", record)
    monkeypatch.setattr("app.routers.help.contact_store.save", fake_save)
    monkeypatch.setattr("app.routers.help.outbox_service.flush_quietly", fake_flush)
    body = {"name": "Ann", "email": "ann@example.com", "message": "Hi"}

    client.post("/help/contact", json=body)

    assert keys == ["rate:contact:ip:testclient", "rate:contact:all"]


def test_contact_messages_need_every_field(client):
    body = {"name": "Ann", "email": "ann@example.com", "message": "Hi"}

    assert client.post("/help/contact", json={**body, "email": "not-an-email"}).status_code == 422
    assert client.post("/help/contact", json={**body, "name": "  "}).status_code == 422
    assert client.post("/help/contact", json={**body, "message": ""}).status_code == 422
