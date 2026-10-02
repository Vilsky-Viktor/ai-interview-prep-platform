import io
import json
from functools import cache

from openai import AsyncOpenAI

from app.constants.generation import LLM_TIMEOUT_SECONDS

COMPLETIONS = "/v1/chat/completions"


@cache
def get_client() -> AsyncOpenAI:
    return AsyncOpenAI(timeout=LLM_TIMEOUT_SECONDS)


async def submit(requests: dict[str, dict]) -> str:
    """Sends chat completion bodies keyed by custom id as one batch; returns its id."""
    lines = [
        json.dumps({"custom_id": custom_id, "method": "POST", "url": COMPLETIONS, "body": body})
        for custom_id, body in requests.items()
    ]
    upload = await get_client().files.create(
        file=("requests.jsonl", io.BytesIO("\n".join(lines).encode())), purpose="batch"
    )
    batch = await get_client().batches.create(
        input_file_id=upload.id, endpoint=COMPLETIONS, completion_window="24h"
    )

    return batch.id


async def status(batch_id: str) -> tuple[str, str | None]:
    """The batch's status and, once completed, the id of its output file."""
    batch = await get_client().batches.retrieve(batch_id)

    return batch.status, batch.output_file_id


async def results(file_id: str) -> dict[str, str | None]:
    """The reply text per custom id; None for a request that failed."""
    content = await get_client().files.content(file_id)
    replies = {}

    for line in content.text.splitlines():
        if not line.strip():
            continue

        item = json.loads(line)
        response = item.get("response") or {}
        body = response.get("body") or {}
        choices = body.get("choices") or [{}]
        reply = choices[0].get("message", {}).get("content")
        replies[item["custom_id"]] = reply if response.get("status_code") == 200 else None

    return replies
