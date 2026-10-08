from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from prepza_common.i18n import request_language
from prepza_common.paging import PageParams

from app.auth import UserWithToken
from app.constants.chat import NOT_FOUND
from app.schemas.conversations import ConversationDetailOut, ConversationOut, MessageOut
from app.services.conversations import open_conversation
from app.storage import conversations, messages

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("")
async def list_conversations(
    auth: UserWithToken, page: PageParams, company_id: UUID | None = None
) -> list[ConversationOut]:
    """The user's conversations, the latest first; about one company when it's given."""
    user, _ = auth
    found = await conversations.of_user(user.uid, company_id, page.offset, page.limit)

    return [ConversationOut.model_validate(item) for item in found]


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: UUID, request: Request, auth: UserWithToken
) -> ConversationDetailOut:
    """One of the user's conversations with its messages. One about a company they can no
    longer see is deleted, and is a 404."""
    user, token = auth
    conversation = await open_conversation(
        conversation_id, user.uid, token, request_language(request)
    )
    found = await messages.of_conversation(conversation.id)

    return ConversationDetailOut(
        **ConversationOut.model_validate(conversation).model_dump(),
        messages=[MessageOut.model_validate(item) for item in found],
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: UUID, auth: UserWithToken) -> None:
    user, _ = auth

    if await conversations.owned(conversation_id, user.uid) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)

    await conversations.delete_one(conversation_id)
