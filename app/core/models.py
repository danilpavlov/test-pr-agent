from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Book(Base):
    """Модель книги в базе данных."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    publication_year = Column(Integer, nullable=True)
    isbn = Column(String(20), nullable=True, unique=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        """
        Представление объекта в виде строки.

        Returns:
            str: Строковое представление объекта
        """
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>" 