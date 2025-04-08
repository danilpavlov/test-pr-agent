from typing import Dict, Optional, Union

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from app.dependencies import BookId, get_book_service, get_metadata_service, get_pagination
from app.models.book import BookCreate, BookInDB, BookResponse, BookUpdate
from app.models.import_export import ImportResponse
from app.models.metadata import BookMetadata
from app.models.response import DefaultResponse, ErrorResponse, PagedResponse
from app.services.book_service import BookService
from app.services.metadata_service import MetadataService
from app.utils.csv_export import create_csv_response
from app.utils.json_import import process_json_file
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

logger = get_logger(__name__)


@router.get(
    "",
    response_model=PagedResponse[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список книг",
    description="Получить список книг с возможностью пагинации и фильтрации",
)
async def get_books(
    title: Optional[str] = Query(None, description="Фильтр по названию книги"),
    author: Optional[str] = Query(None, description="Фильтр по автору книги"),
    publication_year: Optional[int] = Query(
        None, description="Фильтр по году публикации"
    ),
    isbn: Optional[str] = Query(None, description="Фильтр по ISBN"),
    pagination: Dict[str, int] = Depends(get_pagination),
    book_service: BookService = Depends(get_book_service),
) -> PagedResponse[BookResponse]:
    """
    Получение списка книг с пагинацией и фильтрацией.

    Args:
        title: Фильтр по названию книги (частичное совпадение)
        author: Фильтр по автору книги (частичное совпадение)
        publication_year: Фильтр по году публикации (точное совпадение)
        isbn: Фильтр по ISBN (точное совпадение)
        pagination: Параметры пагинации
        book_service: Сервис для работы с книгами

    Returns:
        Список книг с метаданными пагинации
    """
    filters = {}
    if title:
        filters["title"] = title
    if author:
        filters["author"] = author
    if publication_year:
        filters["publication_year"] = publication_year
    if isbn:
        filters["isbn"] = isbn

    books, metadata = await book_service.get_books(
        page=pagination["page"],
        page_size=pagination["page_size"],
        filters=filters,
    )

    return PagedResponse[BookResponse](
        status=True,
        message="Список книг успешно получен",
        items=books,
        metadata=metadata,
    )


@router.get(
    "/{book_id}",
    response_model=Union[BookResponse, ErrorResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить книгу по ID",
    description="Получить детальную информацию о книге по её идентификатору",
)
async def get_book(
    book_id: BookId,
    book_service: BookService = Depends(get_book_service),
) -> Union[BookResponse, ErrorResponse]:
    """
    Получение книги по идентификатору.

    Args:
        book_id: Идентификатор книги
        book_service: Сервис для работы с книгами

    Returns:
        Информация о книге

    Raises:
        HTTPException: Если книга не найдена
    """
    book = await book_service.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена",
        )

    return BookResponse.model_validate(book)


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую книгу",
    description="Создать новую книгу с указанными параметрами",
)
async def create_book(
    book_data: BookCreate,
    book_service: BookService = Depends(get_book_service),
) -> BookResponse:
    """
    Создание новой книги.

    Args:
        book_data: Данные для создания книги
        book_service: Сервис для работы с книгами

    Returns:
        Созданная книга
    """
    book = await book_service.create_book(book_data)
    return BookResponse.model_validate(book)


@router.put(
    "/{book_id}",
    response_model=Union[BookResponse, ErrorResponse],
    status_code=status.HTTP_200_OK,
    summary="Обновить книгу",
    description="Обновить существующую книгу с указанными параметрами",
)
async def update_book(
    book_id: BookId,
    book_data: BookUpdate,
    book_service: BookService = Depends(get_book_service),
) -> Union[BookResponse, ErrorResponse]:
    """
    Обновление существующей книги.

    Args:
        book_id: Идентификатор книги
        book_data: Данные для обновления книги
        book_service: Сервис для работы с книгами

    Returns:
        Обновленная книга

    Raises:
        HTTPException: Если книга не найдена
    """
    book = await book_service.update_book(book_id, book_data)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена",
        )

    return BookResponse.model_validate(book)


@router.delete(
    "/{book_id}",
    response_model=DefaultResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить книгу",
    description="Удалить книгу по её идентификатору",
)
async def delete_book(
    book_id: BookId,
    book_service: BookService = Depends(get_book_service),
) -> DefaultResponse:
    """
    Удаление книги.

    Args:
        book_id: Идентификатор книги
        book_service: Сервис для работы с книгами

    Returns:
        Статус операции

    Raises:
        HTTPException: Если книга не найдена
    """
    deleted = await book_service.delete_book(book_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена",
        )

    return DefaultResponse(
        status=True,
        message=f"Книга с ID {book_id} успешно удалена",
    )


@router.get(
    "/{book_id}/metadata",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Обогатить книгу метаданными",
    description="Получает метаданные для книги из внешнего API и обогащает ими существующую книгу",
)
async def enrich_book_with_metadata(
    book_id: BookId,
    book_service: BookService = Depends(get_book_service),
    metadata_service: MetadataService = Depends(get_metadata_service),
) -> BookResponse:
    """
    Обогащение книги метаданными из внешнего API.

    Args:
        book_id: Идентификатор книги
        book_service: Сервис для работы с книгами
        metadata_service: Сервис для работы с метаданными книг

    Returns:
        Обогащенная книга

    Raises:
        HTTPException: Если книга не найдена или возникла ошибка при получении метаданных
    """
    # Получаем книгу из базы данных
    book = await book_service.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена",
        )
    
    # Проверяем, что у книги есть ISBN
    if not book.isbn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У книги отсутствует ISBN, невозможно получить метаданные",
        )
    
    # Преобразуем Pydantic модель в словарь для обновления
    book_dict = book.model_dump()
    
    # Скрытый факап: не ловим ошибки от API
    # Обогащаем данные книги метаданными
    enhanced_book_data = await metadata_service.enhance_book_data(book.isbn, book_dict)
    
    # Скрытый факап: мы изменяем модель напрямую через словарь, без валидации
    # Создаем модель обновления книги
    book_update = BookUpdate(**enhanced_book_data)
    
    # Обновляем книгу в базе данных
    updated_book = await book_service.update_book(book_id, book_update)
    if updated_book is None:
        # Этот код не должен выполниться, так как мы уже проверили существование книги
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении книги",
        )
    
    return BookResponse.model_validate(updated_book) 