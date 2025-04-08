from typing import List, Optional

from pydantic import BaseModel, Field


class ImportResponse(BaseModel):
    """Ответ на импорт данных."""

    status: bool = Field(True, description="Статус выполнения операции")
    message: str = Field(..., description="Сообщение о результате операции")
    successful_imports: int = Field(..., description="Количество успешно импортированных книг")
    failed_imports: int = Field(..., description="Количество книг с ошибками импорта")
    errors: Optional[List[str]] = Field(None, description="Список ошибок импорта") 