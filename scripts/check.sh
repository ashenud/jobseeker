#!/usr/bin/env bash
set -euo pipefail
docker compose --profile dev run --rm --no-deps api python scripts/validate_docs.py
docker compose --profile dev run --rm --no-deps api python scripts/validate_milestone.py --all
docker compose --profile dev run --rm --no-deps api python scripts/validate_codex_controls.py
docker compose --profile dev run --rm --no-deps api ruff check .
docker compose --profile dev run --rm --no-deps api mypy src
docker compose --profile dev run --rm --no-deps api pytest -q
