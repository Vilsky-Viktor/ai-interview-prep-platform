import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.helpers.talents import suggestions

CLOSE = uuid.uuid4()
FAR = uuid.uuid4()
START = datetime(2026, 10, 5, 9, tzinfo=UTC)


def section(user, template, round_id, right, minutes, status="finished"):
    """A practice section of four questions, `right` of them answered right."""
    return SimpleNamespace(
        user_id=user,
        interview_set_id=template,
        candidate_invite_id=round_id,
        started_at=START + timedelta(minutes=minutes),
        status=status,
        questions=[{}] * 4,
        answers=[SimpleNamespace(score=100 if i < right else 0) for i in range(4)],
    )


def link(name):
    return SimpleNamespace(name=name, url=f"https://www.linkedin.com/in/{name}")


def test_only_a_finished_first_round_at_the_bar_counts_best_first():
    rows = [
        # Ann: 75% first on the close template; a later 100% doesn't count.
        section("ann", CLOSE, "a1", 3, 0),
        section("ann", CLOSE, "a2", 4, 60),
        # Bob: 100% first round.
        section("bob", FAR, "b1", 4, 0),
        # Cleo: 50%, under the bar.
        section("cleo", CLOSE, "c1", 2, 0),
        # Dan: his first round isn't finished; a later finished one doesn't count.
        section("dan", CLOSE, "d1", 4, 0, status="in_progress"),
        section("dan", CLOSE, "d2", 4, 60),
    ]
    links = {user: link(user) for user in ("ann", "bob", "cleo", "dan")}

    found = suggestions(rows, links, [CLOSE, FAR])

    assert [(talent.name, talent.grade) for talent in found] == [("bob", 100), ("ann", 75)]
