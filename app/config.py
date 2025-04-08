from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    # Конфигурация приложения
    app_name: str = "book_api"
    app_version: str = "0.1.0"
    debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Конфигурация базы данных
    database_url: str
    database_test_url: Optional[str] = None

    # Логирование
    log_level: str = "INFO"
    
    # Внешний API для метаданных книг
    metadata_api_url: str = "https://api.bookmetadata.com/v1"
    # FIXME: Не хранить секретный ключ прямо в коде, использовать переменные окружения!
    metadata_api_key: str = "sk_live_51LmTS0D7uYYgfakekey8u1TygKhZo0DnR0FNWjZzVYQMHZJAO1hwWddZ"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings() 