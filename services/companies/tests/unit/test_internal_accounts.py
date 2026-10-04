from prepza_common.service_auth import issue_token

from app.storage import companies

URL = "/internal/users/ann/companies"


def test_notifications_gets_every_company_of_a_user(client, monkeypatch):
    asked = []

    async def fake_ids(user_id):
        asked.append(user_id)

        return ["acme", "globex"]

    monkeypatch.setattr(companies, "ids_for_user", fake_ids)
    token = issue_token("notifications", "companies", "test-secret-that-is-at-least-32-bytes")

    response = client.get(URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"company_ids": ["acme", "globex"]}
    assert asked == ["ann"]


def test_the_companies_of_a_user_need_a_service_token(client):
    assert client.get(URL).status_code in (401, 403)
