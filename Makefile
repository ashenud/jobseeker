.PHONY: bootstrap check test lint type up down migrate seed db-reset test-integration eval release-check
bootstrap:
	python -m pip install -e .[dev]
check: lint type test
lint:
	ruff check .
type:
	mypy src
test:
	pytest
up:
	docker compose --profile core --profile workers up -d --build
down:
	docker compose --profile core --profile workers down
migrate:
	alembic upgrade head
seed:
	job-agent seed
db-reset:
	@echo "Use docker compose down -v && docker compose up before migrate in local dev"
test-integration:
	pytest tests -q
eval:
	job-agent eval run
release-check:
	job-agent release check
