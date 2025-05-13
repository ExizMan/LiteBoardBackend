.PHONY: up down build migrate migrate-down migrate-up ps logs

# Запуск всех сервисов в режиме разработки
up:
	docker compose up --build --watch

# Остановка всех сервисов
down:
	docker compose down

# Пересборка и запуск всех сервисов
build:
	docker compose up -d --build

# Запуск всех миграций
migrate:
	docker compose up -d db
	docker compose run --rm migrations alembic revision --autogenerate -m "auto migration"
	docker compose run --rm migrations alembic upgrade head
	docker compose down


# Откат всех миграций
migrate-down:
	docker compose run --rm migrations alembic downgrade base

# Создание новой миграции (требуется указать имя: make migrate-revision name=my_migration)
migrate-revision:
	docker compose run --rm migrations alembic revision --autogenerate -m "$(name)"

# Просмотр статуса контейнеров
ps:
	docker compose ps

# Просмотр логов (можно указать сервис: make logs service=auth)
logs:
	docker compose logs $(service) -f

# Очистка всех данных (включая volumes)
clean:
	docker compose down -v
