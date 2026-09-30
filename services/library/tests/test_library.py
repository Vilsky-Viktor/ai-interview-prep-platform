from app.storage import search


def test_library_search_is_public(client, monkeypatch):
    async def fake_search(text):
        assert text == "python"

        return []

    monkeypatch.setattr(search, "search_public", fake_search)

    assert client.get("/library", params={"q": "python"}).status_code == 200


def test_search_matches_title():
    compiled = str(search._matches("acme").compile()).lower()

    assert "like" in compiled
    assert "sets.title" in compiled
