import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from prepza_common.analytics import track
from prepza_common.auth import OptionalUser
from prepza_common.constants import DAY_SECONDS, HOUR_SECONDS
from prepza_common.i18n import request_language, translate
from prepza_common.rate_limit import hit

from app.config.settings import settings
from app.constants.faq import FAQS
from app.constants.help import LegalDocument
from app.constants.legal import LEGAL_UPDATED
from app.constants.privacy import PRIVACY_INTRO, PRIVACY_SECTIONS
from app.constants.rounds import CHAT_FAILED
from app.constants.terms import TERMS_INTRO, TERMS_SECTIONS
from app.helpers.help import faq_items
from app.helpers.sse import sse_event
from app.integrations import billing
from app.integrations.redis import get_redis
from app.schemas.help import FaqItemOut, HelpChatRequest, LegalOut
from app.services.help import build_messages, stream_reply

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/help", tags=["help"])

DOCUMENTS = {
    LegalDocument.TERMS: (TERMS_INTRO, TERMS_SECTIONS),
    LegalDocument.PRIVACY: (PRIVACY_INTRO, PRIVACY_SECTIONS),
}


@router.get("/faq")
async def get_faq(request: Request) -> list[FaqItemOut]:
    """The FAQ in the page's language, with today's prices; public."""
    items = faq_items(FAQS[request_language(request)], await billing.catalog())

    return [FaqItemOut(**item) for item in items]


@router.get("/legal/{document}")
async def get_legal(document: LegalDocument) -> LegalOut:
    """The terms or the privacy policy, in English only; public."""
    intro, sections = DOCUMENTS[document]

    return LegalOut(intro=intro, updated=LEGAL_UPDATED, sections=sections)


@router.post("/chat")
async def help_chat(
    body: HelpChatRequest, request: Request, user: OptionalUser
) -> StreamingResponse:
    """Answers questions about prepza, for visitors too. Streams server-sent events:
    {"delta"}..., then {"done"} or {"error"}."""
    redis = get_redis()

    if user:
        await hit(redis, f"rate:help:{user.uid}", settings.help_user_limit, HOUR_SECONDS)

    await hit(redis, "rate:help:all", settings.help_daily_limit, DAY_SECONDS)

    language = request_language(request)
    messages = build_messages(body.messages, language, await billing.catalog())

    async def events():
        try:
            async for delta in stream_reply(messages):
                yield sse_event({"delta": delta})
        except Exception:
            logger.exception("Help chat failed")
            yield sse_event({"error": translate(CHAT_FAILED, language)})

            return

        await track("help_chat_turn", user_id=user.uid if user else None, turn=len(body.messages))

        yield sse_event({"done": True})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        # Tells nginx not to buffer the stream.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
