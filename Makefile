.PHONY: bootstrap check test lint type typecheck pre-commit up down logs migrate migration-check seed db-reset test-integration eval release-check
bootstrap:
	docker compose --profile dev build
check:
	docker compose --profile dev run --rm api sh -c 'python scripts/validate_docs.py && python scripts/validate_milestone.py --all && python scripts/validate_codex_controls.py && ruff check . && mypy src && pytest -q && pre-commit run --all-files && alembic upgrade head && alembic downgrade base && alembic upgrade head && test "$$(alembic current | cut -d" " -f1)" = "0001_initial"'
lint:
	docker compose --profile dev run --rm --no-deps api ruff check .
type:
	docker compose --profile dev run --rm --no-deps api mypy src
typecheck:
	docker compose --profile dev run --rm --no-deps api mypy src
test:
	docker compose --profile dev run --rm --no-deps api pytest -q
pre-commit:
	docker compose --profile dev run --rm --no-deps api pre-commit run --all-files
up:
	docker compose --profile dev up -d --build
down:
	docker compose --profile dev down
logs:
	docker compose --profile dev logs --follow
migrate:
	docker compose --profile dev run --rm api alembic upgrade head
migration-check:
	docker compose --profile dev run --rm api sh -c 'alembic upgrade head && alembic downgrade base && alembic upgrade head && test "$$(alembic current | cut -d" " -f1)" = "0001_initial"'
seed:
	docker compose --profile dev run --rm api job-agent seed
db-reset:
	docker compose --profile dev down -v
	docker compose --profile dev up -d --build
	docker compose --profile dev run --rm api alembic upgrade head
test-integration:
	docker compose --profile dev run --rm -e JOB_AGENT_RUN_INTEGRATION=true api pytest -q -m integration
eval:
	docker compose --profile dev run --rm api job-agent eval run
release-check:
	docker compose --profile dev run --rm api job-agent release check
