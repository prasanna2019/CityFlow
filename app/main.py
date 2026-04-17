from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException

from app.exceptions.common_exceptions import (
    AppExceptions,
    app_exception_handler,
    http_exception_handler,
)
from app.routes.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        timeout=10.0,
    )
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(AppExceptions, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.include_router(user_router)
