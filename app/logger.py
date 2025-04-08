import sys
from pathlib import Path
from typing import Dict, Union

from loguru import logger

from app.config import settings


def setup_logging() -> None:
    """Настройка логирования для приложения."""
    log_level = settings.log_level

    # Удаление дефолтного обработчика
    logger.remove()

    # Настройка формата логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Добавление обработчика для консоли
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True,
    )

    # Добавление обработчика для файла
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)

    logger.add(
        log_path / "app.log",
        format=log_format,
        level=log_level,
        rotation="10 MB",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    logger.debug("Логирование настроено")


def get_logger(name: str) -> "logger":
    """
    Получить логгер с указанным именем.

    Args:
        name: Имя логгера

    Returns:
        Объект логгера
    """
    return logger.bind(name=name) 