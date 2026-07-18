.PHONY: bootstrap check test lint type pre-commit up down migrate seed db-reset test-integration eval release-check
bootstrap:
	docker compose --profile dev build api
check: lint type test
lint:
	docker compose --profile dev run --rm --no-deps api ruff check .
type:
	docker compose --profile dev run --rm --no-deps api mypy src
test:
	docker compose --profile dev run --rm --no-deps api pytest -q
pre-commit:
	docker compose --profile dev run --rm --no-deps api pre-commit run --all-files
up:
	docker compose --profile dev up -d --build
down:
	docker compose --profile dev down
migrate:
	docker compose --profile dev run --rm api alembic upgrade head
seed:
	docker compose --profile dev run --rm api job-agent seed
db-reset:
	docker compose --profile dev down -v
	docker compose --profile dev up -d --build
	docker compose --profile dev run --rm api alembic upgrade head
test-integration:
	docker compose --profile dev run --rm api pytest tests -q
eval:
	docker compose --profile dev run --rm api job-agent eval run
release-check:
	docker compose --profile dev run --rm api job-agent release check
