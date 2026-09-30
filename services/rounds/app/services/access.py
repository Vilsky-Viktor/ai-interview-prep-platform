from uuid import UUID

from fastapi import HTTPException, status

from app.models.rounds import Answer, Round
from app.schemas.user import User
from app.storage import answers, rounds


async def get_owned_round(round_id: UUID, user: User) -> Round:
    round_ = await rounds.get(round_id)

    if round_ is None or round_.user_id != user.uid:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Round not found")

    return round_


async def get_owned_answer(answer_id: UUID, user: User) -> tuple[Answer, Round]:
    answer = await answers.get(answer_id)
    round_ = await rounds.get(answer.round_id) if answer else None

    if round_ is None or round_.user_id != user.uid:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Answer not found")

    return answer, round_
