.PHONY: up down build test lint format install clean

# Запуск проекта
up:
	docker-compose up -d

# Остановка проекта
down:
	docker-compose down

# Сборка проекта
build:
	docker-compose build

# Запуск тестов
test:
	pytest

# Проверка кода
lint:
	pre-commit run --all-files

# Форматирование кода
format:
	isort app tests
	black app tests

# Установка зависимостей
install:
	poetry install

# Очистка
clean:
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -type d -name *.eggs -exec rm -rf {} +
	find . -type f -name *.pyc -delete
	find . -type f -name *.pyo -delete
	find . -type f -name *.pyd -delete 