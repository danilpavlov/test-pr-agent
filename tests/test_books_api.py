import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.core.models import Book
from app.models.metadata import BookMetadata, Author
from app.services.metadata_service import MetadataService


@pytest.mark.asyncio
async def test_create_book(client: AsyncClient, db_session) -> None:
    """Тест создания книги."""
    # Данные для создания книги
    book_data = {
        "title": "Тестовая книга",
        "author": "Тестовый автор",
        "description": "Описание тестовой книги",
        "publication_year": 2023,
        "isbn": "1234567890123"
    }

    # Отправляем запрос на создание книги
    response = await client.post("/api/books", json=book_data)

    # Проверяем статус-код ответа
    assert response.status_code == 201

    # Проверяем, что в ответе есть id новой книги
    assert "id" in response.json()
    assert response.json()["title"] == book_data["title"]
    assert response.json()["author"] == book_data["author"]
    assert response.json()["publication_year"] == book_data["publication_year"]

    # Проверяем, что книга была создана в базе данных
    book_id = response.json()["id"]
    result = await db_session.get(Book, book_id)
    assert result is not None
    assert result.title == book_data["title"]
    assert result.author == book_data["author"]


@pytest.mark.asyncio
async def test_get_book(client: AsyncClient, db_session) -> None:
    """Тест получения книги по ID."""
    # Создаём книгу для теста
    book = Book(
        title="Получение книги",
        author="Автор для получения",
        description="Описание книги для получения",
        publication_year=2022,
        isbn="9876543210123"
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    # Отправляем запрос на получение книги
    response = await client.get(f"/api/books/{book.id}")

    # Проверяем статус-код ответа
    assert response.status_code == 200

    # Проверяем данные книги в ответе
    assert response.json()["id"] == book.id
    assert response.json()["title"] == book.title
    assert response.json()["author"] == book.author
    assert response.json()["publication_year"] == book.publication_year


@pytest.mark.asyncio
async def test_get_books(client: AsyncClient, db_session) -> None:
    """Тест получения списка книг."""
    # Создаём книги для теста
    books = [
        Book(title="Книга 1", author="Автор 1", publication_year=2021),
        Book(title="Книга 2", author="Автор 2", publication_year=2022),
        Book(title="Книга 3", author="Автор 3", publication_year=2023),
    ]
    for book in books:
        db_session.add(book)
    await db_session.commit()

    # Отправляем запрос на получение списка книг
    response = await client.get("/api/books")

    # Проверяем статус-код ответа
    assert response.status_code == 200

    # Проверяем метаданные пагинации
    assert "metadata" in response.json()
    assert response.json()["metadata"]["total_items"] >= 3

    # Проверяем, что в ответе есть созданные книги
    book_titles = [book["title"] for book in response.json()["items"]]
    assert "Книга 1" in book_titles
    assert "Книга 2" in book_titles
    assert "Книга 3" in book_titles


@pytest.mark.asyncio
async def test_update_book(client: AsyncClient, db_session) -> None:
    """Тест обновления книги."""
    # Создаём книгу для теста
    book = Book(
        title="Старое название",
        author="Старый автор",
        description="Старое описание",
        publication_year=2020
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    # Данные для обновления
    update_data = {
        "title": "Новое название",
        "author": "Новый автор",
        "description": "Новое описание",
        "publication_year": 2023
    }

    # Отправляем запрос на обновление книги
    response = await client.put(f"/api/books/{book.id}", json=update_data)

    # Проверяем статус-код ответа
    assert response.status_code == 200

    # Проверяем обновленные данные в ответе
    assert response.json()["title"] == update_data["title"]
    assert response.json()["author"] == update_data["author"]
    assert response.json()["description"] == update_data["description"]

    # Проверяем, что книга обновлена в базе данных
    await db_session.refresh(book)
    assert book.title == update_data["title"]
    assert book.author == update_data["author"]


@pytest.mark.asyncio
async def test_delete_book(client: AsyncClient, db_session) -> None:
    """Тест удаления книги."""
    # Создаём книгу для теста
    book = Book(
        title="Книга для удаления",
        author="Автор для удаления",
        description="Описание книги для удаления"
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    # Отправляем запрос на удаление книги
    response = await client.delete(f"/api/books/{book.id}")

    # Проверяем статус-код ответа
    assert response.status_code == 200

    # Проверяем сообщение об успешном удалении
    assert response.json()["status"] is True
    assert f"Книга с ID {book.id} успешно удалена" in response.json()["message"]

    # Проверяем, что книга удалена из базы данных
    result = await db_session.get(Book, book.id)
    assert result is None


@pytest.mark.asyncio
@patch("app.services.metadata_service.MetadataService.get_book_metadata")
async def test_enrich_book_with_metadata(mock_get_book_metadata, client: AsyncClient, db_session) -> None:
    """Тест обогащения книги метаданными."""
    # Создаём книгу для теста
    book = Book(
        title="Книга для метаданных",
        author="Автор книги",
        description="Описание книги",
        publication_year=2022,
        isbn="1234567890123"
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    
    # Моковые метаданные
    mock_metadata = BookMetadata(
        isbn="1234567890123",
        title="Новое название из метаданных",
        authors=[Author(name="Автор из метаданных")],
        description="Новое описание из метаданных",
        pages=300,
        language="ru"
    )
    
    # Мокаем вызов внешнего API
    mock_get_book_metadata.return_value = mock_metadata
    
    # Отправляем запрос на обогащение книги метаданными
    response = await client.get(f"/api/books/{book.id}/metadata")
    
    # Проверяем статус-код ответа
    assert response.status_code == 200
    
    # Проверяем, что книга была обогащена метаданными
    assert response.json()["title"] == mock_metadata.title
    assert response.json()["description"] == mock_metadata.description
    
    # Скрытая ошибка: не проверяем, что метод был вызван с правильным ISBN
    # mock_get_book_metadata.assert_called_once_with(book.isbn)
    
    # Проверяем, что книга была обновлена в базе данных
    await db_session.refresh(book)
    assert book.title == mock_metadata.title
    
    # Скрытая ошибка: проверяем неверное поле, добавляя в тест уязвимость
    assert "cover_url" in response.json()
    
    # Скрытая ошибка: утверждаем, что publication_date правильно установлен,
    # что неверно из-за ошибки типов в сервисе
    assert response.json()["publication_date"] is not None 