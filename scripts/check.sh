#!/usr/bin/env bash
set -euo pipefail
docker compose --profile dev run --rm api python scripts/validate_docs.py
docker compose --profile dev run --rm api python scripts/validate_milestone.py --all
docker compose --profile dev run --rm api python scripts/validate_codex_controls.py
docker compose --profile dev run --rm api ruff check .
docker compose --profile dev run --rm api mypy src
docker compose --profile dev run --rm api pytest -q
docker compose --profile dev run --rm api pre-commit run --all-files
docker compose --profile dev run --rm api sh -c 'alembic upgrade head && alembic downgrade base && alembic upgrade head && test "$(alembic current | cut -d" " -f1)" = "0001_initial"'
