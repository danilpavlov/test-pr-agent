import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.database import Base, get_async_session
from app.main import app


# Использование тестовой базы данных
TEST_DATABASE_URL = settings.database_test_url or (
    settings.database_url.replace("/book_api", "/book_api_test")
)
ASYNC_TEST_DATABASE_URL = TEST_DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Создает экземпляр цикла событий для тестов.

    Yields:
        Цикл событий для асинхронных тестов
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_app() -> AsyncGenerator[FastAPI, None]:
    """
    Создает экземпляр FastAPI для тестирования.

    Yields:
        Экземпляр приложения FastAPI
    """
    yield app


@pytest_asyncio.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    """
    Создает и настраивает тестовую базу данных.

    Yields:
        None
    """
    # Создаем асинхронный движок для работы с базой данных
    engine = create_async_engine(ASYNC_TEST_DATABASE_URL)

    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Удаляем все данные и таблицы после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    setup_database,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Создает сессию базы данных для тестов.

    Args:
        setup_database: Фикстура для настройки базы данных

    Yields:
        Экземпляр асинхронной сессии базы данных
    """
    engine = create_async_engine(ASYNC_TEST_DATABASE_URL)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    test_app: FastAPI, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """
    Создает асинхронный HTTP-клиент для тестирования API.

    Args:
        test_app: Экземпляр FastAPI
        db_session: Экземпляр сессии базы данных

    Yields:
        Асинхронный HTTP-клиент
    """

    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear() 