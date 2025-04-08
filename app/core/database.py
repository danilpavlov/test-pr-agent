from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# URL базы данных в асинхронном формате
SQLALCHEMY_DATABASE_URL = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Создание асинхронного движка базы данных
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=settings.debug)

# Создание асинхронной сессии
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Создание базового класса для моделей SQLAlchemy
Base = declarative_base()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения асинхронной сессии базы данных.

    Yields:
        AsyncSession: Асинхронная сессия базы данных
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise 