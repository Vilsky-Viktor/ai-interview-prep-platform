import json

from prepza_common.constants import LEGAL_VERSIONS

from app.helpers import legal


def test_every_current_text_is_kept_as_its_version():
    """A changed text needs a new version: python -m app.legal_archive keeps it."""
    for document, version in LEGAL_VERSIONS.items():
        kept = json.loads((legal.ARCHIVE / document / f"{version}.json").read_text())

        assert kept == legal.current(document), f"{document} changed: give it a new version"


def test_a_document_is_read_as_any_version_ever_published(client, tmp_path, monkeypatch):
    (tmp_path / "terms").mkdir()
    (tmp_path / "terms" / "2026-01-01.json").write_text(
        json.dumps({"intro": "Old terms.", "sections": []})
    )
    (tmp_path / "terms" / f"{LEGAL_VERSIONS['terms']}.json").write_text("{}")
    monkeypatch.setattr(legal, "ARCHIVE", tmp_path)

    now = client.get("/help/legal/terms").json()
    old = client.get("/help/legal/terms", params={"version": "2026-01-01"}).json()

    assert now["version"] == now["current"] == LEGAL_VERSIONS["terms"]
    assert now["versions"] == [LEGAL_VERSIONS["terms"], "2026-01-01"]
    assert (old["intro"], old["version"], old["current"]) == (
        "Old terms.",
        "2026-01-01",
        LEGAL_VERSIONS["terms"],
    )
    assert client.get("/help/legal/terms", params={"version": "1999-01-01"}).status_code == 404


def test_a_version_published_ahead_applies_from_its_day(tmp_path, monkeypatch):
    (tmp_path / "terms").mkdir()

    for name in ("2026-01-01", "2026-06-01", "2999-01-01"):
        (tmp_path / "terms" / f"{name}.json").write_text("{}")

    monkeypatch.setattr(legal, "ARCHIVE", tmp_path)

    assert legal.in_force("terms") == "2026-06-01"
    assert [
        legal.state(name, "2026-06-01") for name in ("2026-01-01", "2026-06-01", "2999-01-01")
    ] == [
        "replaced",
        "in_force",
        "upcoming",
    ]
