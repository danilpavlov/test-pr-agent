from typing import Annotated, Dict, Optional

from fastapi import Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.services.book_service import BookService


async def get_book_service(
    session: AsyncSession = Depends(get_async_session),
) -> BookService:
    """
    Зависимость для получения сервиса работы с книгами.

    Args:
        session: Асинхронная сессия базы данных

    Returns:
        Сервис для работы с книгами
    """
    return BookService(session)


async def get_pagination(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
) -> Dict[str, int]:
    """
    Зависимость для параметров пагинации.

    Args:
        page: Номер страницы (начиная с 1)
        page_size: Размер страницы (от 1 до 100)

    Returns:
        Словарь с параметрами пагинации
    """
    return {"page": page, "page_size": page_size}


BookId = Annotated[int, Path(..., title="ID книги", ge=1)] 