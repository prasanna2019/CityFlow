import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from redis.asyncio import from_url

from app.db import init_db
from app.exceptions.common_exceptions import (
    AppExceptions,
    app_exception_handler,
    http_exception_handler,
)
from app.routes.user import router as user_router

REDIS_URL = os.getenv("redis_url", "redis://localhost:6379/0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        timeout=10.0,
    )
    app.state.redis_client = from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        await init_db()
        yield
    finally:
        await app.state.http_client.aclose()
        await app.state.redis_client.aclose()


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(AppExceptions, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.include_router(user_router)
