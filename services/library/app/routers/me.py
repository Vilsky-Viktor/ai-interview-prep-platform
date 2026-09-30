from fastapi import APIRouter

from app.auth import CurrentUser
from app.schemas.user import User

router = APIRouter()


@router.get("/me")
def me(user: CurrentUser) -> User:
    return user
