from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.auth import CurrentUser
from app.constants.sets import Access
from app.schemas.feedback import PreparationRatingIn
from app.services.access import access_for, require_member
from app.storage import feedback, joins, preparations

router = APIRouter(prefix="/preparations", tags=["joins"])


@router.post("/{preparation_id}/join", status_code=status.HTTP_204_NO_CONTENT)
async def join(preparation_id: UUID, user: CurrentUser) -> None:
    """Joins a public preparation; owners and members are already in."""
    question_set = await preparations.get(preparation_id)
    access = await access_for(question_set, user.uid) if question_set else None

    if access is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Preparation not found")

    if access == Access.PUBLIC:
        await joins.join(preparation_id, user.uid)


@router.delete("/{preparation_id}/join", status_code=status.HTTP_204_NO_CONTENT)
async def leave(preparation_id: UUID, user: CurrentUser) -> None:
    question_set = await preparations.get(preparation_id)
    access = await access_for(question_set, user.uid) if question_set else None

    if access == Access.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can't leave your own preparation")

    await joins.leave(preparation_id, user.uid)


@router.put("/{preparation_id}/rating", status_code=status.HTTP_204_NO_CONTENT)
async def rate(preparation_id: UUID, body: PreparationRatingIn, user: CurrentUser) -> None:
    """Joined users rate the preparation; owners can't rate their own."""
    access = await require_member(await preparations.get(preparation_id), user.uid)

    if access == Access.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can't rate your own preparation")

    if not await feedback.rate_preparation(preparation_id, user.uid, body.value):
        raise HTTPException(status.HTTP_409_CONFLICT, "Already rated")
