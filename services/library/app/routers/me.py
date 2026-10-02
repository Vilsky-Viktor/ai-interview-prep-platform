from fastapi import APIRouter
from prepza_common.auth import CurrentUser
from prepza_common.user import User

router = APIRouter()


@router.get("/me")
def me(user: CurrentUser) -> User:
    return user
