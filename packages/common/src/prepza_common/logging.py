import json
import logging
import os
import time
from contextvars import ContextVar
from datetime import UTC, datetime

from prepza_common.constants import TRACE_FIELD, TRACE_HEADER
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# The trace of the request being served, as Cloud Logging names it; None outside a request.
current_trace: ContextVar[str | None] = ContextVar("current_trace", default=None)


class JsonFormatter(logging.Formatter):
    """One JSON object per line, in the fields Cloud Logging reads: its severity, so errors are
    errors there, and the request's trace, when there is one."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        trace = current_trace.get()

        if trace:
            payload[TRACE_FIELD] = trace

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def trace_of(header: str | None) -> str | None:
    """The request's trace from the load balancer's header, as Cloud Logging names it; None
    without the header or outside Google Cloud."""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    trace_id = (header or "").split("/")[0]

    if not project or not trace_id:
        return None

    return f"projects/{project}/traces/{trace_id}"


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
    """Logs each request's line, and ties every line logged while serving it to its trace."""

    async def dispatch(self, request: Request, call_next):
        token = current_trace.set(trace_of(request.headers.get(TRACE_HEADER)))
        start = time.perf_counter()

        try:
            response = await call_next(request)
            elapsed_ms = round((time.perf_counter() - start) * 1000)
            logging.getLogger("http").info(
                "%s %s %s %dms",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )
        finally:
            current_trace.reset(token)

        return response
