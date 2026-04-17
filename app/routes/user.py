import os

import httpx
from app.dependencies import get_http_client
from app.exceptions.common_exceptions import AppExceptions
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query, status

load_dotenv()

router = APIRouter(prefix="/user", tags=["user"])

BASE_URL = os.getenv("base_url")


def _build_url(path: str, city: str) -> str:
    if not BASE_URL:
        raise AppExceptions(
            message="base_url is not configured in the environment.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}?city={city}"


@router.get("/weather")
async def get_weather(
    city: str = Query(..., min_length=1, description="City name"),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    return {
        "service": "weather",
        "city": city,
        "upstream_url": _build_url("weather", city),
        "client_ready": not client.is_closed,
        "message": "Tentative weather endpoint created successfully.",
    }


@router.get("/sport")
async def get_sport(
    city: str = Query(..., min_length=1, description="City name"),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    return {
        "service": "sport",
        "city": city,
        "upstream_url": _build_url("sport", city),
        "client_ready": not client.is_closed,
        "message": "Tentative sport endpoint created successfully.",
    }
