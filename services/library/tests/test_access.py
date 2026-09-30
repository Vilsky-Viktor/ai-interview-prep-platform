import asyncio
import uuid

import pytest
from fastapi import HTTPException

from app.constants.sets import Access, SetKind, Visibility
from app.models.sets import QuestionSet
from app.services import access
from app.storage import joins


def question_set(visibility=Visibility.PRIVATE, kind=SetKind.PREPARATION):
    return QuestionSet(id=uuid.uuid4(), kind=kind, owner_id="owner", visibility=visibility)


@pytest.fixture
def joined(monkeypatch):
    members = set()

    async def fake_is_joined(set_id, user_id):
        return user_id in members

    monkeypatch.setattr(joins, "is_joined", fake_is_joined)

    return members


@pytest.mark.parametrize(
    ("visibility", "user_id", "expected"),
    [
        (Visibility.PRIVATE, "owner", Access.OWNER),
        (Visibility.PRIVATE, "member", Access.JOINED),
        (Visibility.PRIVATE, "stranger", None),
        (Visibility.PRIVATE, None, None),
        (Visibility.PUBLIC, "stranger", Access.PUBLIC),
        (Visibility.PUBLIC, None, Access.PUBLIC),
    ],
)
def test_access_for(joined, visibility, user_id, expected):
    joined.add("member")

    assert asyncio.run(access.access_for(question_set(visibility), user_id)) == expected


def test_interviews_are_never_accessible(joined):
    interview = question_set(Visibility.PUBLIC, SetKind.INTERVIEW)

    assert asyncio.run(access.access_for(interview, "owner")) is None


def test_public_visitors_must_join_before_practicing(joined):
    with pytest.raises(HTTPException) as error:
        asyncio.run(access.require_member(question_set(Visibility.PUBLIC), "stranger"))

    assert error.value.status_code == 404
