
SHELL := /bin/bash

up:
	docker compose up -d --build

down:
	docker compose down -v

migrate:
	docker compose exec api bash -lc "alembic upgrade head"

seed:
	docker compose exec api bash -lc "python -m src.scripts.seed"

worker:
	docker compose exec api bash -lc "celery -A src.worker.celery_app worker -l info"

web:
	docker compose exec web bash -lc "npm run dev"
