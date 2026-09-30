from functools import cache

from tavily import AsyncTavilyClient


@cache
def get_tavily() -> AsyncTavilyClient:
    return AsyncTavilyClient()
