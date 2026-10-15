import pytest

from app.constants.invites import ALREADY_FINISHED, InviteStatus
from app.helpers.candidates import row_actions
from app.main import app
from app.storage import invites
from tests.unit.test_candidate_invites import URL, invite_setup


def test_a_finished_candidate_is_not_invited_again(client, monkeypatch):
    sent, used = invite_setup(monkeypatch)

    async def finished(_interview_id, _email):
        return InviteStatus.FINISHED, "key"

    monkeypatch.setattr(invites, "held", finished)

    response = client.post(URL, json={"email": "carol@example.com"})
    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == ALREADY_FINISHED
    assert sent == used == []


@pytest.mark.parametrize(
    ("status", "can_resend", "revokable"),
    [
        (InviteStatus.INVITED, True, True),
        (InviteStatus.EXPIRED, True, True),
        (InviteStatus.IN_PROCESS, True, False),
        (InviteStatus.FINISHED, False, False),
        (InviteStatus.DELETED, False, False),
    ],
)
def test_the_server_says_what_each_candidate_allows(status, can_resend, revokable):
    assert row_actions(status) == {"can_resend": can_resend, "revokable": revokable}
