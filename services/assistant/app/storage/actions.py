import json
from uuid import UUID

from app.constants.actions_flow import ACTION_KEY, ACTION_TTL_SECONDS, USER_ACTIONS_KEY
from app.integrations.redis import get_redis


def key(action_id: UUID) -> str:
    return ACTION_KEY.format(action_id=action_id)


async def save(action_id: UUID, pending: dict) -> None:
    """A prepared action, for ACTION_TTL_SECONDS: whose it is (user, conversation, company), the
    tool and its exact arguments."""
    mine = USER_ACTIONS_KEY.format(user_id=pending["user_id"])

    async with get_redis().pipeline(transaction=True) as pipe:
        pipe.set(key(action_id), json.dumps(pending), ex=ACTION_TTL_SECONDS)
        pipe.sadd(mine, str(action_id))
        pipe.expire(mine, ACTION_TTL_SECONDS)
        await pipe.execute()


async def peek(action_id: UUID) -> dict | None:
    found = await get_redis().get(key(action_id))

    return json.loads(found) if found else None


async def claim(action_id: UUID) -> dict | None:
    """Takes the action, atomically: of two confirms (or a confirm and a cancel), only one gets
    it; None when it's gone (handled, or expired)."""
    found = await get_redis().getdel(key(action_id))

    return json.loads(found) if found else None


async def put_back(action_id: UUID, pending: dict) -> None:
    """Gives a claimed action back when it couldn't run at all (the user's token had expired),
    unless it was prepared again meanwhile."""
    await get_redis().set(key(action_id), json.dumps(pending), ex=ACTION_TTL_SECONDS, nx=True)


async def delete_user(user_id: str) -> None:
    """Every pending action of the user's (deleting their account). Safe to repeat."""
    redis = get_redis()
    mine = USER_ACTIONS_KEY.format(user_id=user_id)
    ids = await redis.smembers(mine)
    await redis.delete(mine, *(ACTION_KEY.format(action_id=item.decode()) for item in ids))
