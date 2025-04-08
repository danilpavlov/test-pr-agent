from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class BookBase(BaseModel):
    """Базовая модель для книги."""

    title: str = Field(..., title="Название книги", max_length=255)
    author: str = Field(..., title="Автор книги", max_length=255)
    description: Optional[str] = Field(None, title="Описание книги")
    publication_year: Optional[int] = Field(
        None,
        title="Год публикации",
        ge=1000,
        le=datetime.now().year,
    )
    isbn: Optional[str] = Field(
        None, title="ISBN", max_length=20, pattern=r"^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$"
    )

    @validator("publication_year")
    def validate_publication_year(cls, v: Optional[int]) -> Optional[int]:
        """
        Валидация года публикации.

        Args:
            v: Год публикации

        Returns:
            Валидный год публикации

        Raises:
            ValueError: Если год публикации некорректный
        """
        if v is not None and (v < 1000 or v > datetime.now().year):
            raise ValueError(
                f"Год публикации должен быть от 1000 до {datetime.now().year}"
            )
        return v


class BookCreate(BookBase):
    """Модель для создания книги."""

    pass


class BookUpdate(BookBase):
    """Модель для обновления книги."""

    title: Optional[str] = Field(None, title="Название книги", max_length=255)
    author: Optional[str] = Field(None, title="Автор книги", max_length=255)


class BookInDB(BookBase):
    """Модель книги в базе данных."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Конфигурация модели."""

        from_attributes = True
        populate_by_name = True


class BookResponse(BookInDB):
    """Модель ответа с книгой."""

    pass 