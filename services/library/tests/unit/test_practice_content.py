import uuid
from types import SimpleNamespace

from app.storage import preparations
from tests.unit.test_internal import token

TEMPLATE_ID = uuid.uuid4()


def question(stage, text):
    return SimpleNamespace(
        id=uuid.uuid4(),
        text=text,
        stage=stage,
        options=[{"answer": "a", "correct": True}, {"answer": "b", "correct": False}],
    )


def test_practice_gets_only_revealed_questions_and_skips_empty_topics(client, monkeypatch):
    template = SimpleNamespace(
        id=TEMPLATE_ID,
        kind="template",
        title="Backend",
        topics=[
            SimpleNamespace(
                id=uuid.uuid4(),
                title="Python",
                questions=[question("revealed", "Open?"), question("private", "Secret?")],
            ),
            SimpleNamespace(id=uuid.uuid4(), title="SQL", questions=[question("private", "S?")]),
        ],
    )

    async def get_content(set_id):
        return template if set_id == TEMPLATE_ID else None

    monkeypatch.setattr(preparations, "get_content", get_content)
    headers = {"Authorization": f"Bearer {token()}"}

    found = client.get(f"/internal/templates/{TEMPLATE_ID}/practice", headers=headers).json()
    missing = client.get(f"/internal/templates/{uuid.uuid4()}/practice", headers=headers)

    assert [topic["title"] for topic in found["topics"]] == ["Python"]
    assert [q["text"] for q in found["topics"][0]["questions"]] == ["Open?"]
    assert missing.status_code == 404
