from fastapi import Request


def client_ip(request: Request) -> str:
    """The visitor's address. Google's load balancer appends "<client>,<load balancer>" to
    X-Forwarded-For, after whatever the visitor sent, so the client is the second entry from
    the end; anything earlier can be made up. Without that (locally), the connection's address.
    """
    entries = [part.strip() for part in request.headers.get("x-forwarded-for", "").split(",")]

    if len(entries) >= 2 and entries[-2]:
        return entries[-2]

    return request.client.host if request.client else "unknown"
