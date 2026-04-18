import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.exceptions.common_exceptions import AppExceptions
from app.user import Base, SignUpRequest, User

load_dotenv()

DATABASE_URL = os.getenv(
    "database_url",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/weather_app",
)

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, payload: SignUpRequest, hashed_password: str) -> User:
        user = User(
            name=payload.name,
            email=payload.email,
            password=hashed_password,
        )
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as exc:
            await self.session.rollback()
            raise AppExceptions(
                message="User with this email already exists.",
                status_code=status.HTTP_409_CONFLICT,
            ) from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise AppExceptions(
                message="Unable to create user at the moment.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from exc

    async def get_user_by_email(self, email: str) -> User | None:
        try:
            result = await self.session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise AppExceptions(
                message="Unable to read user data at the moment.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from exc


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(session)


async def init_db() -> None:
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    except SQLAlchemyError as exc:
        raise AppExceptions(
            message="Unable to initialize the database.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc
