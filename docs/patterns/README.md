# Coding Patterns and Standards

These pattern files define the implementation rules Codex must read before working on milestones. They convert the architecture and compliance requirements into repeatable coding standards.

| Order | Pattern | Applies to |
|---:|---|---|
| 00 | [`00-codex-execution.md`](00-codex-execution.md) | Every milestone prompt and Codex run |
| 01 | [`01-docker-local-environment.md`](01-docker-local-environment.md) | Docker Compose, services, local startup, database/Redis |
| 02 | [`02-python-project-standards.md`](02-python-project-standards.md) | Python package layout, typing, linting, public APIs |
| 03 | [`03-fastapi-dashboard.md`](03-fastapi-dashboard.md) | FastAPI routes, Jinja, HTMX/local JavaScript |
| 04 | [`04-database-migrations.md`](04-database-migrations.md) | SQLAlchemy, Alembic, PostgreSQL, pgvector |
| 05 | [`05-configuration-secrets.md`](05-configuration-secrets.md) | Pydantic settings, YAML config, secrets, examples |
| 06 | [`06-policy-compliance.md`](06-policy-compliance.md) | Platform policy registry, external I/O, submissions |
| 07 | [`07-background-jobs.md`](07-background-jobs.md) | Celery, Redis, idempotency, schedules, retries |
| 08 | [`08-llm-and-retrieval.md`](08-llm-and-retrieval.md) | LLM gateway, structured outputs, evidence retrieval |
| 09 | [`09-testing-quality-gates.md`](09-testing-quality-gates.md) | pytest, Ruff, mypy, fixtures, evaluations |
| 10 | [`10-observability-operations.md`](10-observability-operations.md) | Logs, metrics, cost controls, backup/recovery |
