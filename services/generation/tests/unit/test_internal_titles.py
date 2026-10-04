from app.routers import internal_titles
from app.schemas.titles import TitleCheckOut
from app.service_auth import service_token


def headers():
    return {"Authorization": f"Bearer {service_token('generation')}"}


def test_library_learns_whether_a_title_names_a_company(client, monkeypatch):
    asked = []

    async def fake_check(title):
        asked.append(title)

        return TitleCheckOut(has_company="Acme" in title)

    monkeypatch.setattr(internal_titles, "check_title", fake_check)

    named = client.post(
        "/internal/titles/check", json={"title": "Accountant at Acme"}, headers=headers()
    )
    plain = client.post("/internal/titles/check", json={"title": "Accountant"}, headers=headers())

    assert named.json() == {"has_company": True}
    assert plain.json() == {"has_company": False}
    assert asked == ["Accountant at Acme", "Accountant"]


def test_only_services_can_check_titles(client):
    assert client.post("/internal/titles/check", json={"title": "Accountant"}).status_code in (
        401,
        403,
    )
