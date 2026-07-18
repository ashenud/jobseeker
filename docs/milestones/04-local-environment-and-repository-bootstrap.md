# Milestone 04 - Local Environment and Repository Bootstrap

## Goal

Create a reproducible Windows development environment using WSL 2 and Docker Desktop, plus a repository skeleton Codex can safely extend.

## Assumptions

- Windows 10/11 with virtualization enabled.
- WSL 2 with Ubuntu.
- Docker Desktop using the WSL 2 engine.
- Project files stored inside the Linux filesystem, such as `~/projects/freelance-job-agent`, rather than a Windows-mounted path, to avoid file-system performance problems.

## Required deliverables

- `pyproject.toml`
- `uv.lock` or an approved lockfile
- `compose.yaml`
- `Dockerfile`
- `.dockerignore`, `.gitignore`, `.editorconfig`
- `.env.example`
- `src/job_agent/` package skeleton
- `tests/` skeleton
- `scripts/bootstrap.sh`, `scripts/check.sh`, `scripts/dev.sh`
- `Makefile` or `justfile` with equivalent commands
- pre-commit configuration
- CI-like local checks

## Recommended repository layout

```text
src/job_agent/
  api/
  cli/
  core/
  policy/
  db/
  sources/
  normalization/
  scoring/
  knowledge/
  proposals/
  review/
  submission/
  crm/
  workers/
  observability/
config/
data/private/
data/exports/
docs/adr/
scripts/
tests/unit/
tests/integration/
tests/e2e/
```

## Service baseline

- `api`: FastAPI local web/API service.
- `worker`: Celery worker.
- `scheduler`: Celery beat.
- `postgres`: PostgreSQL with pgvector.
- `redis`: queue and short-lived cache.

Do not add Elasticsearch, Kubernetes, React, n8n, or a second vector database in the MVP.

## Dependency baseline

Use a single `pyproject.toml` with explicit groups:

- runtime: FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy, Alembic, psycopg, Celery, Redis client, HTTPX, feedparser, Jinja2, pgvector, OpenAI SDK;
- development: pytest, pytest-asyncio, pytest-cov, respx, Ruff, mypy, pre-commit, freezegun;
- optional: Telegram library and Playwright only when their milestone enables them.

## Required commands

```bash
make bootstrap
make up
make down
make logs
make migrate
make test
make lint
make typecheck
make check
```

Equivalent commands may use `just`, but the user-facing names must remain simple.

## Health endpoints

Create minimal endpoints only:

- `/health/live` - process is running.
- `/health/ready` - database and Redis reachable.
- `/version` - application version and commit, no secrets.

## Development safety

- No live API calls in tests.
- `.env` and `data/private/` ignored.
- Default binds to `127.0.0.1`, not all interfaces.
- Database and Redis ports need not be exposed to the LAN.
- Use named Docker volumes.
- Add resource limits appropriate for local use.

## Verification

From a clean clone in WSL:

```bash
cp .env.example .env
make bootstrap
make up
make migrate
make check
curl http://127.0.0.1:8000/health/ready
```

## Codex execution prompt

```text
Implement Milestone 04 only. Build a minimal typed Python repository with Docker Compose services for FastAPI, Celery worker/beat, PostgreSQL+pgvector, and Redis. Add health endpoints and local check scripts. Do not implement business features. Run the clean-start verification and report exact commands and results.
```

## Acceptance criteria

- [ ] Clean setup works from documented commands.
- [ ] API, worker, scheduler, database, and Redis start.
- [ ] Liveness and readiness behave correctly.
- [ ] Lint, type-check, and tests pass.
- [ ] Secrets/private data are ignored.
- [ ] Services bind locally by default.
