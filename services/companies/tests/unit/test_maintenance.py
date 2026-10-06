import httpx
import pytest
from prepza_common.auth import current_user, optional_user
from prepza_common.user import User

from app.main import app
from app.routers import maintenance as maintenance_routes

ANN = User(uid="ann", email="ann@example.com", email_verified=True)
BOB = User(uid="bob", email="bob@example.com", email_verified=True)


@pytest.fixture(autouse=True)
def switch(monkeypatch):
    """The switch in memory, ann a superadmin and rounds counting 2; returns the turns made."""
    state = {"on": True}
    turns = []

    async def is_on(redis):
        return state["on"]

    async def set_on(redis, on, user_id):
        state["on"] = on
        turns.append((on, user_id))

    async def two():
        return 2

    monkeypatch.setattr(maintenance_routes, "is_on", is_on)
    monkeypatch.setattr(maintenance_routes, "set_on", set_on)
    monkeypatch.setattr(maintenance_routes.rounds, "running_interviews", two)
    monkeypatch.setenv("SUPERADMIN_EMAILS", "ann@example.com")
    yield turns
    app.dependency_overrides.clear()


def signed_in(user):
    app.dependency_overrides[current_user] = lambda: user
    app.dependency_overrides[optional_user] = lambda: user


def test_anyone_reads_the_switch_and_learns_if_the_site_stays_open_to_them(client):
    assert client.get("/maintenance").json() == {"on": True, "superadmin": False}

    signed_in(BOB)

    assert client.get("/maintenance").json() == {"on": True, "superadmin": False}

    signed_in(ANN)

    assert client.get("/maintenance").json() == {"on": True, "superadmin": True}


def test_only_a_superadmin_reads_the_running_count_and_turns_it(client, switch):
    signed_in(BOB)

    assert client.get("/superadmin/maintenance").status_code == 404
    assert client.put("/superadmin/maintenance", json={"on": False}).status_code == 404

    signed_in(ANN)

    assert client.get("/superadmin/maintenance").json() == {"on": True, "running": 2}
    assert client.put("/superadmin/maintenance", json={"on": False}).json() == {
        "on": False,
        "running": 2,
    }
    assert switch == [(False, "ann")]


def test_the_switch_works_while_rounds_is_down(client, monkeypatch):
    async def down():
        raise httpx.ConnectError("rounds is down")

    monkeypatch.setattr(maintenance_routes.rounds, "running_interviews", down)
    signed_in(ANN)

    assert client.get("/superadmin/maintenance").json() == {"on": True, "running": None}
