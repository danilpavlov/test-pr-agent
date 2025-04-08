import json
from typing import Dict, List, Optional, Tuple, Union

from fastapi import HTTPException, UploadFile, status
from pydantic import ValidationError

from app.models.book import BookCreate
from app.services.book_service import BookService
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def validate_json_book(book_data: Dict) -> BookCreate:
    """
    Валидирует данные книги из JSON.

    Args:
        book_data: Данные книги из JSON

    Returns:
        Объект BookCreate с валидными данными

    Raises:
        ValidationError: Если данные не соответствуют схеме
    """
    try:
        return BookCreate(**book_data)
    except ValidationError as e:
        logger.error(f"Ошибка валидации данных книги: {e}")
        raise e


async def process_json_file(
    file: UploadFile, book_service: BookService
) -> Tuple[int, int, List[str]]:
    """
    Обрабатывает JSON-файл и импортирует книги в базу данных.

    Args:
        file: Загруженный файл
        book_service: Сервис для работы с книгами

    Returns:
        Кортеж из количества успешно импортированных книг, 
        количества книг с ошибками и списка ошибок

    Raises:
        HTTPException: Если файл не является JSON или имеет неверный формат
    """
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Загруженный файл должен быть в формате JSON",
        )

    content = await file.read()
    try:
        json_data = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректный JSON-файл: {str(e)}",
        )

    # Проверяем, является ли JSON массивом или одиночным объектом
    if isinstance(json_data, dict):
        json_data = [json_data]
    elif not isinstance(json_data, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JSON должен содержать массив книг или одну книгу",
        )

    successful_imports = 0
    failed_imports = 0
    errors = []

    for idx, book_data in enumerate(json_data):
        try:
            # Валидируем данные книги
            book_create = await validate_json_book(book_data)
            
            # Создаем книгу в базе данных
            await book_service.create_book(book_create)
            
            successful_imports += 1
            logger.debug(f"Книга успешно импортирована: {book_create.title}")
        except ValidationError as e:
            failed_imports += 1
            error_msg = f"Ошибка валидации книги #{idx + 1}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        except Exception as e:
            failed_imports += 1
            error_msg = f"Ошибка импорта книги #{idx + 1}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)

    logger.info(
        f"Импорт завершен. Успешно: {successful_imports}, с ошибками: {failed_imports}"
    )
    return successful_imports, failed_imports, errors 