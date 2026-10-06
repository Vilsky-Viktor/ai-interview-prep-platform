import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.main import app
from app.storage import stats


@pytest.fixture
def signed_in(monkeypatch):
    monkeypatch.setenv("SUPERADMIN_EMAILS", "ann@example.com")

    def sign_in(email):
        app.dependency_overrides[current_user] = lambda: User(
            uid=email, email=email, email_verified=True
        )

    yield sign_in
    app.dependency_overrides.clear()


def test_superadmin_gets_the_counts_of_the_month_asked(client, monkeypatch, signed_in):
    asked = []

    async def counts(month):
        asked.append(month)

        return {"practice": 5}

    monkeypatch.setattr(stats, "stats", counts)
    signed_in("ann@example.com")

    body = client.get("/superadmin/stats?month=2026-10").json()

    assert asked == ["2026-10"]
    assert body["counts"] == {"practice": 5}


def test_without_a_month_the_counts_are_all_time(client, monkeypatch, signed_in):
    asked = []

    async def counts(month):
        asked.append(month)

        return {}

    monkeypatch.setattr(stats, "stats", counts)
    signed_in("ann@example.com")

    assert client.get("/superadmin/stats").status_code == 200
    assert asked == [None]


@pytest.mark.parametrize("month", ["2026-13", "2026-1", "october"])
def test_a_month_that_isnt_one_is_refused(client, signed_in, month):
    signed_in("ann@example.com")

    assert client.get(f"/superadmin/stats?month={month}").status_code == 422


def test_stats_are_not_found_for_others(client, signed_in):
    signed_in("eve@example.com")

    assert client.get("/superadmin/stats?month=2026-10").status_code == 404
