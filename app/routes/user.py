import os

import httpx
from app.api_calls import create_api_task
from app.auth import hash_password, verify_password
from app.config.cache import build_cache_key, get_or_set_cached_service_data
from app.dependencies import get_http_client
from app.dependencies import get_redis_client
from app.db import UserRepository, get_user_repository
from app.exceptions.common_exceptions import AppExceptions
from app.user import LoginRequest, SignUpRequest, UserResponse
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query, status
from redis.asyncio import Redis

load_dotenv()

router = APIRouter(prefix="/user", tags=["user"])

BASE_URL = os.getenv("base_url")
CACHE_USER_ID = "anonymous"


def _build_url(path: str, city: str) -> str:
    if not BASE_URL:
        raise AppExceptions(
            message="base_url is not configured in the environment.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}?city={city}"


async def _fetch_service_from_api(
    service_name: str, city: str, client: httpx.AsyncClient
) -> dict:
    try:
        response = await create_api_task(
            client=client,
            method="GET",
            url=_build_url(service_name, city),
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise AppExceptions(
            message=f"{service_name.title()} API returned an error response.",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.HTTPError as exc:
        raise AppExceptions(
            message=f"Unable to fetch {service_name} data from upstream API.",
            status_code=status.HTTP_502_BAD_GATEWAY,
        ) from exc

    return response.json()


async def _get_service_data(
    service_name: str,
    city: str,
    client: httpx.AsyncClient,
    redis_client: Redis,
) -> dict:
    cache_key = build_cache_key(CACHE_USER_ID, city)
    payload, source = await get_or_set_cached_service_data(
        redis_client=redis_client,
        cache_key=cache_key,
        service_name=service_name,
        fetcher=lambda: _fetch_service_from_api(service_name, city, client),
    )
    return {
        "service": service_name,
        "city": city,
        "cache_key": cache_key,
        "source": source,
        "data": payload,
    }


@router.post("/signin", status_code=status.HTTP_201_CREATED)
async def signin(
    payload: SignUpRequest,
    user_repository: UserRepository = Depends(get_user_repository),
):
    user = await user_repository.create_user(
        payload=payload,
        hashed_password=hash_password(payload.password),
    )

    return {
        "message": "User registered successfully.",
        "user": UserResponse.model_validate(user),
    }


@router.post("/login")
async def login(
    payload: LoginRequest,
    user_repository: UserRepository = Depends(get_user_repository),
):
    user = await user_repository.get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password):
        raise AppExceptions(
            message="Invalid email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return {
        "message": "Login successful.",
        "user": UserResponse.model_validate(user),
    }


@router.get("/weather")
async def get_weather(
    city: str = Query(..., min_length=1, description="City name"),
    client: httpx.AsyncClient = Depends(get_http_client),
    redis_client: Redis = Depends(get_redis_client),
):
    return await _get_service_data("weather", city, client, redis_client)


@router.get("/sport")
async def get_sport(
    city: str = Query(..., min_length=1, description="City name"),
    client: httpx.AsyncClient = Depends(get_http_client),
    redis_client: Redis = Depends(get_redis_client),
):
    return await _get_service_data("sport", city, client, redis_client)
