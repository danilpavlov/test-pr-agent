from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class DefaultResponse(BaseModel):
    """Стандартный ответ API."""

    status: bool = Field(True, description="Статус выполнения операции")
    message: Optional[str] = Field(None, description="Сообщение о результате операции")


class ErrorResponse(DefaultResponse):
    """Ответ API с ошибкой."""

    status: bool = Field(False, description="Статус выполнения операции")
    error: str = Field(..., description="Сообщение об ошибке")
    error_details: Optional[Dict[str, Any]] = Field(
        None, description="Дополнительные детали ошибки"
    )


class PaginationMetadata(BaseModel):
    """Метаданные пагинации."""

    current_page: int = Field(..., description="Текущая страница", ge=1)
    page_size: int = Field(..., description="Размер страницы", ge=1)
    total_items: int = Field(..., description="Общее количество элементов", ge=0)
    total_pages: int = Field(..., description="Общее количество страниц", ge=0)
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_previous: bool = Field(..., description="Есть ли предыдущая страница")


class PagedResponse(DefaultResponse, Generic[T]):
    """Ответ API с пагинацией."""

    items: List[T] = Field(..., description="Элементы на текущей странице")
    metadata: PaginationMetadata = Field(..., description="Метаданные пагинации") 