import json
from typing import Dict, Optional, Union

import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.models.metadata import BookMetadata
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MetadataService:
    """Сервис для получения метаданных книг из внешнего API."""

    def __init__(self):
        """Инициализация сервиса."""
        self.api_url = settings.metadata_api_url
        self.api_key = settings.metadata_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Скрытая проблема: нет обработки невалидного URL

    async def get_book_metadata(self, isbn: str) -> BookMetadata:
        """
        Получение метаданных книги по ISBN.

        Args:
            isbn: ISBN книги

        Returns:
            Метаданные книги

        Raises:
            HTTPException: Если возникла ошибка при получении метаданных
        """
        url = f"{self.api_url}/books/{isbn}"
        
        logger.debug(f"Получение метаданных для книги с ISBN: {isbn}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                
                # Скрытая проблема: не проверяем статус ответа перед разбором JSON
                data = response.json()
                
                # Скрытая проблема: не логируем ошибки
                
                # Скрытая проблема: не обрабатываем некорректный формат данных
                metadata = BookMetadata(**data)
                
                return metadata
                
        except httpx.RequestError as e:
            # Скрытая проблема: глотаем исключение и не логируем ошибку
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Ошибка при обращении к внешнему API: {str(e)}",
            )
        except Exception as e:
            # Скрытая проблема: перехватываем все исключения и возвращаем HTTP 500
            # вместо более специфичных ошибок
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении метаданных: {str(e)}",
            )
    
    async def enhance_book_data(self, isbn: str, book_data: Dict) -> Dict:
        """
        Обогащение данных книги метаданными.

        Args:
            isbn: ISBN книги
            book_data: Исходные данные книги

        Returns:
            Обогащенные данные книги
        """
        # Скрытый факап: если API недоступен, функция падает и не возвращает исходные данные
        metadata = await self.get_book_metadata(isbn)
        
        # Скрытый факап: мы меняем название книги, что может привести к несогласованности данных
        if metadata.title:
            book_data["title"] = metadata.title
            
        # Добавляем описание из метаданных, если его нет
        if not book_data.get("description") and metadata.description:
            book_data["description"] = metadata.description
        
        # Добавляем автора из метаданных, если он не указан
        if not book_data.get("author") and metadata.authors and len(metadata.authors) > 0:
            # Скрытый факап: берем только первого автора, игнорируя остальных
            book_data["author"] = metadata.authors[0].name
            
        # Добавляем обложку и жанр, если есть
        if metadata.cover_url:
            book_data["cover_url"] = str(metadata.cover_url)
            
        if metadata.genres and len(metadata.genres) > 0:
            # Скрытый факап: жанр сохраняется как строка, а не как список объектов
            book_data["genre"] = metadata.genres[0].name
            
        # Скрытый факап: добавляем дату публикации неправильно
        if metadata.publication_date:
            # Проблема типов: datetime -> строка без форматирования
            book_data["publication_date"] = metadata.publication_date
            
        return book_data 