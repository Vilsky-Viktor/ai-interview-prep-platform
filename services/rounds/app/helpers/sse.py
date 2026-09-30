import json


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"
