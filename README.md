# Book API

REST API на FastAPI для управления книгами с использованием PostgreSQL.

## Функциональность

- CRUD операции с книгами
- Асинхронная работа с базой данных через SQLAlchemy
- Валидация данных с помощью Pydantic
- Тестирование с использованием pytest
- Поддержка Docker и Docker Compose
- Миграции базы данных с помощью Alembic

## Структура проекта

```
.
|-- .dockerignore
|-- .env
|-- .gitignore
|-- .pre-commit-config.yaml     # Конфигурация которая используется для проверки кода
|-- Dockerfile
|-- Makefile
|-- README.md
|-- docker-compose.yml
|-- pyproject.toml
|-- pytest.ini
|-- alembic/                    # Миграции базы данных
|-- .devcontainer/              # Конфигурация для разработки в devcontainer'е
|   |-- Dockerfile.dev
|   |-- devcontainer.json
|   `-- docker-compose.dev.yml
|-- app/                        # Исходный код приложения
|   |-- __init__.py
|   |-- config.py               # Конфигурация приложения
|   |-- dependencies.py         # Зависимости для FastAPI
|   |-- main.py                 # Точка входа приложения
|   |-- logger.py               # Настройка логирования
|   |-- api/                    # API приложения
|   |   |-- __init__.py
|   |   `-- books.py            # API для работы с книгами
|   |-- core/                   # Ядро приложения
|   |   |-- __init__.py
|   |   |-- database.py         # Конфигурация базы данных
|   |   `-- models.py           # SQLAlchemy модели
|   |-- models/                 # Pydantic модели
|   |   |-- __init__.py
|   |   |-- book.py             # Модели для книг
|   |   `-- response.py         # Модели ответов API
|   |-- services/               # Бизнес-логика приложения
|   |   |-- __init__.py
|   |   `-- book_service.py     # Сервис для работы с книгами
|   `-- utils/                  # Утилиты приложения
|       |-- __init__.py
|       `-- logger.py           # Вспомогательные функции для логирования
`-- tests/                      # Тесты приложения
    |-- conftest.py             # Конфигурация тестов
    `-- test_books_api.py       # Тесты API книг
```

## Запуск проекта

### Локальная разработка

1. Клонировать репозиторий
2. Создать и активировать виртуальное окружение:
   ```
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows
   ```
3. Установить зависимости:
   ```
   pip install poetry
   poetry install
   ```
4. Настроить файл `.env` (можно скопировать из `.env.example`)
5. Запустить базу данных:
   ```
   docker-compose up -d db
   ```
6. Применить миграции:
   ```
   alembic upgrade head
   ```
7. Запустить приложение:
   ```
   uvicorn app.main:app --reload
   ```

### Запуск через Docker Compose

1. Клонировать репозиторий
2. Настроить файл `.env` (можно скопировать из `.env.example`)
3. Запустить приложение:
   ```
   docker-compose up -d
   ```

### Запуск через Dev Container

1. Установить VS Code с расширением Remote - Containers
2. Клонировать репозиторий
3. Открыть проект в VS Code
4. Нажать F1 и выбрать "Remote-Containers: Reopen in Container"

## API Endpoints

API доступно по адресу `http://localhost:8000/api`

- **GET /api/books** - Получение списка книг с пагинацией и фильтрацией
- **GET /api/books/{book_id}** - Получение информации о книге по ID
- **POST /api/books** - Создание новой книги
- **PUT /api/books/{book_id}** - Обновление существующей книги
- **DELETE /api/books/{book_id}** - Удаление книги

Swagger документация доступна по адресу: `http://localhost:8000/api/docs`

## Тестирование

Запуск тестов:

```
pytest
```

## Лицензия

MIT
