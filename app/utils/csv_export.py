import csv
import io
from typing import Dict, List, Optional, Union

from fastapi.responses import StreamingResponse

from app.models.book import BookResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_csv(
    books: List[BookResponse],
    headers: Optional[Dict[str, str]] = None,
) -> io.StringIO:
    """
    Генерирует CSV-файл на основе списка книг.

    Args:
        books: Список книг для экспорта
        headers: Словарь с заголовками CSV (ключ - поле, значение - заголовок)

    Returns:
        StringIO объект с данными CSV
    """
    if headers is None:
        headers = {
            "id": "ID",
            "title": "Название",
            "author": "Автор",
            "description": "Описание",
            "publication_year": "Год публикации",
            "isbn": "ISBN",
            "created_at": "Дата создания",
            "updated_at": "Дата обновления",
        }

    # Создаем буфер для записи CSV
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(
        csv_buffer,
        fieldnames=list(headers.keys()),
        delimiter=',',
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
    )

    # Записываем заголовки
    writer.writerow(headers)

    # Записываем данные
    for book in books:
        row = {}
        book_dict = book.model_dump()
        
        for field in headers.keys():
            if field in book_dict:
                value = book_dict[field]
                # Форматируем даты для лучшей читаемости
                if field in ["created_at", "updated_at"] and value:
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                row[field] = value
            else:
                row[field] = ""
                
        writer.writerow(row)

    # Возвращаем указатель в начало буфера
    csv_buffer.seek(0)
    return csv_buffer


def create_csv_response(
    books: List[BookResponse],
    filename: str = "books_export.csv",
    headers: Optional[Dict[str, str]] = None,
) -> StreamingResponse:
    """
    Создает HTTP-ответ с CSV-файлом.

    Args:
        books: Список книг для экспорта
        filename: Имя файла для скачивания
        headers: Словарь с заголовками CSV (ключ - поле, значение - заголовок)

    Returns:
        StreamingResponse с CSV-файлом
    """
    csv_buffer = generate_csv(books, headers)
    
    logger.debug(f"Экспортировано {len(books)} книг в CSV-формат")
    
    response = StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
    )
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    
    return response 