from fastapi import HTTPException, status

from app.constants.sets import Access, SetKind, Visibility
from app.models.sets import QuestionSet
from app.storage import joins


async def access_for(question_set: QuestionSet, user_id: str | None) -> Access | None:
    """Owner, joined member, or a visitor of a public preparation; None means no access."""
    if question_set.kind != SetKind.PREPARATION:
        return None

    if user_id == question_set.owner_id:
        return Access.OWNER

    if user_id and await joins.is_joined(question_set.id, user_id):
        return Access.JOINED

    if question_set.visibility == Visibility.PUBLIC:
        return Access.PUBLIC

    return None


async def require_member(question_set: QuestionSet | None, user_id: str) -> Access:
    """Owners and joined users can practice, rate and report; everyone else gets a 404."""
    access = await access_for(question_set, user_id) if question_set else None

    if access not in (Access.OWNER, Access.JOINED):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Preparation not found")

    return access


def require_owner(question_set: QuestionSet | None, user_id: str) -> QuestionSet:
    if (
        question_set is None
        or question_set.kind != SetKind.PREPARATION
        or question_set.owner_id != user_id
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Preparation not found")

    return question_set
