import httpx
from fastapi import Request
from fastapi import status
from redis.asyncio import Redis

from app.exceptions.common_exceptions import AppExceptions


def get_http_client(request: Request) -> httpx.AsyncClient:
    client = getattr(request.app.state, "http_client", None)
    if client is None:
        raise AppExceptions(
            message="HTTP client is not available.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return client


def get_redis_client(request: Request) -> Redis:
    client = getattr(request.app.state, "redis_client", None)
    if client is None:
        raise AppExceptions(
            message="Redis client is not available.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return client
