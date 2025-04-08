from math import ceil
from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_

from app.core.models import Book
from app.models.book import BookCreate, BookInDB, BookUpdate
from app.models.response import PaginationMetadata
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BookService:
    """Сервис для работы с книгами."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация сервиса.

        Args:
            session: Асинхронная сессия базы данных
        """
        self.session = session

    async def get_books(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[BookInDB], PaginationMetadata]:
        """
        Получение списка книг с пагинацией и фильтрацией.

        Args:
            page: Номер страницы
            page_size: Размер страницы
            filters: Фильтры для запроса

        Returns:
            Кортеж из списка книг и метаданных пагинации
        """
        # Создание запроса
        query = select(Book)

        # Применение фильтров
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(Book, key) and value is not None:
                    if key in ["title", "author"]:
                        filter_conditions.append(
                            getattr(Book, key).ilike(f"%{value}%")
                        )
                    else:
                        filter_conditions.append(getattr(Book, key) == value)
            if filter_conditions:
                query = query.where(and_(*filter_conditions))

        # Общее количество записей для пагинации
        count_query = select(func.count()).select_from(query.subquery())
        total_items = await self.session.scalar(count_query)

        # Пагинация
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Выполнение запроса
        result = await self.session.execute(query)
        books = result.scalars().all()

        # Создание метаданных пагинации
        total_pages = ceil(total_items / page_size) if total_items > 0 else 0
        metadata = PaginationMetadata(
            current_page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

        logger.debug(f"Получено {len(books)} книг из {total_items}")
        return [BookInDB.model_validate(book) for book in books], metadata

    async def get_book_by_id(self, book_id: int) -> Optional[BookInDB]:
        """
        Получение книги по идентификатору.

        Args:
            book_id: Идентификатор книги

        Returns:
            Объект книги или None, если книга не найдена
        """
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        book = result.scalars().first()

        if book is None:
            logger.debug(f"Книга с id={book_id} не найдена")
            return None

        logger.debug(f"Книга с id={book_id} найдена")
        return BookInDB.model_validate(book)

    async def create_book(self, book_data: BookCreate) -> BookInDB:
        """
        Создание новой книги.

        Args:
            book_data: Данные для создания книги

        Returns:
            Созданный объект книги
        """
        book = Book(**book_data.model_dump())
        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book)

        logger.debug(f"Создана новая книга с id={book.id}")
        return BookInDB.model_validate(book)

    async def update_book(
        self, book_id: int, book_data: BookUpdate
    ) -> Optional[BookInDB]:
        """
        Обновление книги.

        Args:
            book_id: Идентификатор книги
            book_data: Данные для обновления книги

        Returns:
            Обновленный объект книги или None, если книга не найдена
        """
        # Проверяем, что книга существует
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        book = result.scalars().first()

        if book is None:
            logger.debug(f"Книга с id={book_id} не найдена для обновления")
            return None

        # Обновляем только переданные поля
        update_data = {
            k: v for k, v in book_data.model_dump().items() if v is not None
        }
        for key, value in update_data.items():
            setattr(book, key, value)

        await self.session.commit()
        await self.session.refresh(book)

        logger.debug(f"Обновлена книга с id={book.id}")
        return BookInDB.model_validate(book)

    async def delete_book(self, book_id: int) -> bool:
        """
        Удаление книги.

        Args:
            book_id: Идентификатор книги

        Returns:
            True, если книга успешно удалена, иначе False
        """
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        book = result.scalars().first()

        if book is None:
            logger.debug(f"Книга с id={book_id} не найдена для удаления")
            return False

        await self.session.delete(book)
        await self.session.commit()

        logger.debug(f"Удалена книга с id={book_id}")
        return True 