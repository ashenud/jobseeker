# Milestone 04 - Local Environment and Repository Bootstrap

## Recovery gate

The current container stack is not accepted. From clean images and volumes,
`api`, `worker`, `scheduler`, PostgreSQL with pgvector, and Redis must start and
be healthy. Uvicorn binds `0.0.0.0` inside the container while Compose publishes
only `127.0.0.1`; database and Redis are not published. Dependency locking,
Psycopg, ASGI startup, Alembic imports, Celery discovery, and readiness checks
must be real. All `make`/script targets are thin Docker Compose wrappers.

Required evidence includes Compose config, build, start, migrate, containerized
Ruff/mypy/pytest, HTTP liveness/readiness/version, worker ping, and clean teardown.

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


## Acceptance criteria

- **M04-AC01:** The Python 3.12 API/tooling image builds from a real frozen
  dependency lock, contains every required runtime and development dependency,
  and supports the documented repository skeleton without host Python.
- **M04-AC02:** Compose defines operational `api`, `worker`, `scheduler`, `db`
  with pgvector, and `redis` services with bounded local resources and named
  persistence volumes. Uvicorn listens on `0.0.0.0` only inside its container,
  the API publishes only on `127.0.0.1`, and PostgreSQL and Redis publish no host
  ports.
- **M04-AC03:** From fresh containers and volumes all five services become
  healthy, dependency ordering is health-based rather than start-order based,
  and the stack returns to healthy after a restart.
- **M04-AC04:** The real FastAPI/ASGI application serves public HTTP
  `/health/live`, `/health/ready`, and `/version` endpoints. Readiness performs
  bounded PostgreSQL and Redis probes, returns `200` only when both succeed,
  returns `503` with secret-free component status when either fails, and
  liveness remains independent of those dependencies.
- **M04-AC05:** Alembic imports real SQLAlchemy metadata and the configured
  Psycopg PostgreSQL URL, enables pgvector, and completes a fresh
  upgrade/downgrade/upgrade cycle with the expected revision recorded.
- **M04-AC06:** A real Celery application loads through the production worker
  entry point, the worker answers a broker-backed control ping, and the scheduler
  remains healthy with Redis and PostgreSQL available. Full task routing,
  idempotency, and recovery remain owned by Milestone 16.
- **M04-AC07:** Pydantic settings keep source, AI, outreach, and write behavior
  disabled by default; malformed values fail closed; `.env` stays optional; and
  `.env`, private inputs, credentials, and caches are excluded from Git and the
  image build context.
- **M04-AC08:** `make bootstrap`, `up`, `down`, `logs`, `migrate`, `test`,
  `lint`, `typecheck`, and `check`, plus the bootstrap/check/dev scripts, are
  executable thin Docker Compose wrappers. They never resolve dependencies or
  run application tools on the host.
- **M04-AC09:** The containerized documentation/status/Codex validators, Ruff,
  mypy, pre-commit, migration integration checks, and a nonzero full pytest suite
  pass without live external calls while policy controls continue to fail
  closed.
- **M04-AC10:** The tested implementation commit reproduces with fresh images and
  volumes in an isolated clean checkout, the receipt is generated from real
  command results with an empty production-placeholder scan, a separate evidence
  analyst validates every acceptance mapping, and an independent policy/release
  reviewer returns `GO` with no unresolved high or critical finding.
