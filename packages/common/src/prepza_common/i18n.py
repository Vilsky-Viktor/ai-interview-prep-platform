from fastapi import FastAPI, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES
from prepza_common.translations import TRANSLATIONS
from starlette.exceptions import HTTPException

# Pydantic's prefix on messages raised from a validator.
VALUE_ERROR = "Value error, "


def language_of(accept_language: str) -> str:
    """The interface language in an Accept-Language header: its first tag, without its region
    ("fil-PH" is Filipino, "pt-BR" Portuguese)."""
    value = accept_language.split(",")[0].split(";")[0]
    value = value.split("-")[0].strip().lower()

    return value if value in LANGUAGES else DEFAULT_LANGUAGE


def request_language(request: Request) -> str:
    """The interface language, which the frontend sends as Accept-Language."""
    return language_of(request.headers.get("accept-language", ""))


def translate(text: str, language: str) -> str:
    return TRANSLATIONS.get(language, {}).get(text, text)


async def localized_http_error(request: Request, error: HTTPException):
    if isinstance(error.detail, str):
        error.detail = translate(error.detail, request_language(request))

    return await http_exception_handler(request, error)


async def localized_validation_error(request: Request, error: RequestValidationError):
    language = request_language(request)

    for item in error.errors():
        message = item.get("msg", "")

        if message.startswith(VALUE_ERROR):
            item["msg"] = VALUE_ERROR + translate(message.removeprefix(VALUE_ERROR), language)

    return await request_validation_exception_handler(request, error)


def add_localized_errors(app: FastAPI) -> None:
    """Error messages in the language of the interface that asked."""
    app.add_exception_handler(HTTPException, localized_http_error)
    app.add_exception_handler(RequestValidationError, localized_validation_error)
