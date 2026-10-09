import logging

from fastapi import HTTPException, Request, status
from openai import OpenAIError
from prepza_common.pause import refuse_if_paused
from prepza_common.secrets_check import SECRET_IN_VOICE, find_secret

from app.config.settings import settings
from app.constants.transcribe import (
    AUDIO_FILES,
    AUDIO_NOT_SUPPORTED,
    AUDIO_TOO_LARGE,
    MAX_AUDIO_BYTES,
    NOTHING_HEARD,
    TRANSCRIBE_FAILED,
    TRANSCRIBE_LANGUAGES,
)
from app.integrations.llm import get_openai
from app.integrations.redis import get_redis
from app.services import limits

logger = logging.getLogger(__name__)


async def read_audio(request: Request) -> bytes:
    """The recording in the request's body, in memory; over MAX_AUDIO_BYTES, a 413 before more
    of it is read."""
    if int(request.headers.get("content-length") or 0) > MAX_AUDIO_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, AUDIO_TOO_LARGE)

    audio = bytearray()

    async for chunk in request.stream():
        audio += chunk

        if len(audio) > MAX_AUDIO_BYTES:
            raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, AUDIO_TOO_LARGE)

    return bytes(audio)


async def transcribe(request: Request, user_id: str, language: str) -> str:
    """A voice message's text, heard in the interface's language. Refused during the pause, over
    the limits, for another format (415) or a larger recording (413); nothing heard is a 422.
    Its tokens count against the user's budgets. The audio and the text are never kept or
    logged."""
    redis = get_redis()
    await refuse_if_paused(redis)
    content_type = request.headers.get("content-type", "").split(";")[0].strip().lower()
    file_name = AUDIO_FILES.get(content_type)

    if file_name is None:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, AUDIO_NOT_SUPPORTED)

    audio = await read_audio(request)

    if not audio:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, NOTHING_HEARD)

    await limits.check_transcription(redis, user_id)

    try:
        result = await get_openai().audio.transcriptions.create(
            model=settings.transcribe_model,
            file=(file_name, audio, content_type),
            language=TRANSCRIBE_LANGUAGES.get(language, language),
        )
    except OpenAIError as error:
        # The error's type only: its message may quote the request.
        logger.warning("A transcription failed: %s", type(error).__name__)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, TRANSCRIBE_FAILED)

    tokens = getattr(getattr(result, "usage", None), "total_tokens", 0) or 0
    await limits.record(redis, user_id, None, tokens)
    text = result.text.strip()

    if not text:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, NOTHING_HEARD)

    # A secret said aloud: its text never comes back.
    if find_secret(text) is not None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, SECRET_IN_VOICE)

    return text
