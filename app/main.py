import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router as api_router
from app.config import settings
from app.logger import setup_logging
from app.models.response import ErrorResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для инициализации и очистки ресурсов при запуске и остановке приложения.

    Args:
        app: Экземпляр FastAPI
    """
    # Настройка логирования
    setup_logging()
    logger.debug("Приложение запускается")

    yield

    logger.debug("Приложение останавливается")


# Создание экземпляра FastAPI
app = FastAPI(
    title=settings.app_name,
    description="FastAPI CRUD API для управления книгами",
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Добавление middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Глобальный обработчик исключений.

    Args:
        request: Объект запроса
        exc: Исключение

    Returns:
        JSONResponse с информацией об ошибке
    """
    logger.exception(f"Необработанное исключение: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status=False,
            error="Внутренняя ошибка сервера",
            error_details={
                "type": type(exc).__name__,
                "message": str(exc),
            },
        ).model_dump(),
    )


# Подключение API роутеров
app.include_router(api_router)


# Корневой эндпоинт
@app.get("/", include_in_schema=False)
async def root():
    """
    Корневой эндпоинт для проверки работоспособности API.

    Returns:
        Информация о сервисе
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
    } 