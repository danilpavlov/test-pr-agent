from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Author(BaseModel):
    """Модель автора книги."""

    name: str = Field(..., description="Имя автора")
    birth_year: Optional[int] = Field(None, description="Год рождения автора")
    death_year: Optional[int] = Field(None, description="Год смерти автора")
    country: Optional[str] = Field(None, description="Страна автора")


class Publisher(BaseModel):
    """Модель издателя книги."""

    name: str = Field(..., description="Название издательства")
    country: Optional[str] = Field(None, description="Страна издательства")
    website: Optional[HttpUrl] = Field(None, description="Веб-сайт издательства")


class Rating(BaseModel):
    """Модель рейтинга книги."""

    average: float = Field(..., description="Средний рейтинг", ge=0, le=5)
    votes: int = Field(..., description="Количество голосов", ge=0)
    source: str = Field(..., description="Источник рейтинга")


class Genre(BaseModel):
    """Модель жанра книги."""

    name: str = Field(..., description="Название жанра")
    category: Optional[str] = Field(None, description="Категория жанра")


class BookMetadata(BaseModel):
    """Модель метаданных книги."""

    isbn: str = Field(..., description="ISBN книги")
    title: str = Field(..., description="Название книги")
    authors: List[Author] = Field(..., description="Авторы книги")
    publisher: Optional[Publisher] = Field(None, description="Издатель книги")
    publication_date: Optional[datetime] = Field(None, description="Дата публикации")
    language: Optional[str] = Field(None, description="Язык книги")
    pages: Optional[int] = Field(None, description="Количество страниц", gt=0)
    cover_url: Optional[HttpUrl] = Field(None, description="URL обложки книги")
    description: Optional[str] = Field(None, description="Описание книги")
    genres: Optional[List[Genre]] = Field(None, description="Жанры книги")
    ratings: Optional[List[Rating]] = Field(None, description="Рейтинги книги")
    
    # Проблема: Не учитываем формат даты при десериализации из JSON 