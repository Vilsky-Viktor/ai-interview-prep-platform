import logging

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse, StreamingResponse
from prepza_common.analytics import track
from prepza_common.auth import OptionalUser
from prepza_common.client_ip import client_ip
from prepza_common.constants import DAY_SECONDS, DEFAULT_LANGUAGE, HOUR_SECONDS, LEGAL_VERSIONS
from prepza_common.human_check import require_human
from prepza_common.i18n import request_language, translate
from prepza_common.pause import refuse_if_paused
from prepza_common.rate_limit import hit
from prepza_common.secrets_check import secret_in
from prepza_common.sse import event_stream, sse_event
from prepza_common.user import Language

from app.config.settings import settings
from app.constants.contact import CONTACT_IP_LIMIT
from app.constants.help import HELP_IP_LIMIT, PRICES_UNAVAILABLE, LegalDocument
from app.constants.legal import NO_SUCH_VERSION
from app.constants.rounds import CHAT_FAILED
from app.helpers import legal
from app.helpers.help import faq_items
from app.helpers.sign_in import secret_reply, with_sign_in
from app.integrations import billing
from app.integrations.redis import get_redis
from app.schemas.contact import ContactRequest
from app.schemas.help import FaqItemOut, HelpChatRequest, LegalOut
from app.services import outbox as outbox_service
from app.services.help import build_messages, platform_guide, stream_reply
from app.storage import contact as contact_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/help", tags=["help"])


@router.get("/faq")
async def get_faq(request: Request) -> list[FaqItemOut]:
    """The FAQ in the page's language, with today's prices; public. Without prices (billing not
    answering) it's refused rather than built with blanks: the site keeps its last good page."""
    catalog = await billing.catalog()

    if catalog is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, PRICES_UNAVAILABLE)

    items = faq_items(request_language(request), catalog)

    return [FaqItemOut(**item) for item in items]


@router.get("/guide", response_class=PlainTextResponse)
async def get_guide(request: Request) -> str:
    """Everything prepza's help chat answers from, as text: how prepza works and how to use it,
    the FAQ in the page's language, today's prices, the terms and the privacy policy; public."""
    return await platform_guide(request_language(request))


@router.get("/legal/{document}")
async def get_legal(
    document: LegalDocument,
    version: str | None = Query(default=None, max_length=10),
    language: Language = DEFAULT_LANGUAGE,
) -> LegalOut:
    """The terms, the privacy policy or the DPA: the current version, or an earlier one, with
    every published version (the day each applies from), in `language` when it's translated
    (the English text is the binding one); public."""
    text = legal.version(document, version)

    if text is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NO_SUCH_VERSION)

    shown = version or LEGAL_VERSIONS[document]
    applies = legal.in_force(document)
    translated = legal.translation(document, shown, language)

    return LegalOut(
        **(translated or text),
        language=language if translated else DEFAULT_LANGUAGE,
        version=shown,
        state=legal.state(shown, applies),
        current=LEGAL_VERSIONS[document],
        in_force=applies,
        versions=legal.versions(document),
    )


@router.post("/chat")
async def help_chat(
    body: HelpChatRequest, request: Request, user: OptionalUser
) -> StreamingResponse:
    """Answers questions about prepza, for visitors too. Streams server-sent events:
    {"delta"}... (and a {"block"} sign-in card when a visitor asks to sign in or sign up), then
    {"done"} or {"error"}. Refused during the emergency pause, as it's AI. A conversation with a
    secret in it (a key, a token, a password) is answered at once, before anything else, with a
    fixed reply ({"removed"} first: the panel drops that message), and nothing of it is used."""
    language = request_language(request)

    if secret_in([message.content for message in body.messages]) is not None:
        return event_stream(secret_reply(language))

    redis = get_redis()
    await refuse_if_paused(redis)

    # A visitor shows they're a person once, with their chat's first message: the chat has no
    # id to remember it by, and the check shows nothing to most people.
    if user is None and len(body.messages) == 1:
        await require_human(request, settings.turnstile_secret_key)

    if user:
        await hit(redis, f"rate:help:{user.uid}", settings.help_user_limit, HOUR_SECONDS)

    await hit(redis, f"rate:help:ip:{client_ip(request)}", HELP_IP_LIMIT, HOUR_SECONDS)
    await hit(redis, "rate:help:all", settings.help_daily_limit, DAY_SECONDS)

    messages = build_messages(body.messages, language, await billing.catalog())

    async def events():
        try:
            async for event in with_sign_in(stream_reply(messages)):
                yield sse_event(event)
        except Exception:
            logger.exception("Help chat failed")
            yield sse_event({"error": translate(CHAT_FAILED, language)})

            return

        await track("help_chat_turn", user_id=user.uid if user else None, turn=len(body.messages))

        yield sse_event({"done": True})

    return event_stream(events())


@router.post("/contact", status_code=status.HTTP_204_NO_CONTENT)
async def contact(body: ContactRequest, request: Request) -> None:
    """The contact page's message; notifications emails it to prepza's inbox. Public, so the
    sender shows they're a person."""
    await require_human(request, settings.turnstile_secret_key)
    redis = get_redis()
    await hit(redis, f"rate:contact:ip:{client_ip(request)}", CONTACT_IP_LIMIT, DAY_SECONDS)
    await hit(redis, "rate:contact:all", settings.contact_daily_limit, DAY_SECONDS)
    await contact_store.save({**body.model_dump(), "language": request_language(request)})
    await outbox_service.flush_quietly()
