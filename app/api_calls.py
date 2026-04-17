import asyncio
from typing import Any, Awaitable

import httpx


async def run_concurrent_tasks(
    *tasks: Awaitable[Any], return_exceptions: bool = False
) -> list[Any]:
    if not tasks:
        return []

    results = await asyncio.gather(
        *tasks, return_exceptions=return_exceptions
    )
    return list(results)


def create_api_task(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    **request_kwargs: Any,
) -> Awaitable[httpx.Response]:
    return client.request(method=method.upper(), url=url, **request_kwargs)
