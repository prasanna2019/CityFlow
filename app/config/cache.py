import json
import os
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable
from zoneinfo import ZoneInfo

from redis.asyncio import Redis
from redis.exceptions import RedisError

APP_TIMEZONE = ZoneInfo(os.getenv("app_timezone", "Asia/Calcutta"))


def build_cache_key(user_id: str, city: str) -> str:
    return f"{user_id}:{city.strip().lower()}"


def get_today_string() -> str:
    return datetime.now(APP_TIMEZONE).date().isoformat()


def get_seconds_until_midnight() -> int:
    now = datetime.now(APP_TIMEZONE)
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    return max(1, int((next_midnight - now).total_seconds()))


async def delete_cache_entry(redis_client: Redis, cache_key: str) -> None:
    try:
        await redis_client.delete(cache_key)
    except RedisError:
        return None


async def get_cached_city_data(
    redis_client: Redis,
    cache_key: str,
) -> dict[str, Any] | None:
    try:
        cached_value = await redis_client.get(cache_key)
    except RedisError:
        return None

    if not cached_value:
        return None

    cached_payload = json.loads(cached_value)
    if cached_payload.get("cache_date") != get_today_string():
        await delete_cache_entry(redis_client, cache_key)
        return None

    return cached_payload


async def set_cached_city_data(
    redis_client: Redis,
    cache_key: str,
    payload: dict[str, Any],
) -> None:
    try:
        await redis_client.set(
            cache_key,
            json.dumps(payload),
            ex=get_seconds_until_midnight(),
        )
    except RedisError:
        return None


async def get_or_set_cached_service_data(
    redis_client: Redis,
    cache_key: str,
    service_name: str,
    fetcher: Callable[[], Awaitable[dict[str, Any]]],
) -> tuple[dict[str, Any], str]:
    cached_payload = await get_cached_city_data(
        redis_client=redis_client,
        cache_key=cache_key,
    )
    services = cached_payload.get("services", {}) if cached_payload else {}
    if service_name in services:
        return services[service_name], "cache"

    payload = await fetcher()
    updated_payload = {
        "cache_date": get_today_string(),
        "services": {
            **services,
            service_name: payload,
        },
    }
    await set_cached_city_data(
        redis_client=redis_client,
        cache_key=cache_key,
        payload=updated_payload,
    )
    return payload, "api"
