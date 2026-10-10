import json
import logging
import time
from datetime import UTC, datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
    # The HTTP client logs every request's full address at INFO, and some addresses are secrets
    # (a company's Slack web hook): only its warnings and errors are kept.
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000)
        logging.getLogger("http").info(
            "%s %s %s %dms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        return response
