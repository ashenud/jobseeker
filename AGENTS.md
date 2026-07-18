# AGENTS.md - Instructions for Codex

## Mission

Build a reliable local application that helps the owner find suitable freelance design work, rank it, generate truthful tailored proposals, review drafts, and track outcomes. The application is not a mass-bidding bot.

## Mandatory workflow

1. Read `IMPLEMENTATION_STATUS.md` and `docs/milestones/00-index.md` before every substantial task.
2. Work on exactly one milestone at a time unless the user explicitly authorizes a dependency fix.
3. Read the complete milestone document before editing code.
4. Create a brief implementation plan and list the files you expect to change.
5. Implement the smallest complete vertical slice required by that milestone.
6. Run all milestone checks plus the repository-wide fast test suite.
7. Show failures honestly. Do not mark a milestone complete with failing checks.
8. Update `IMPLEMENTATION_STATUS.md`, the changelog, and architectural decision records only after acceptance criteria pass.

## Compliance guardrails

- Never implement CAPTCHA solving, fingerprint spoofing, stealth plugins, proxy rotation intended to evade controls, hidden browser automation, or rate-limit evasion.
- Never store platform passwords, browser cookies, session tokens, payment details, or full inbox exports.
- Do not scrape or automate a platform unless `config/platform_policy.yaml` explicitly permits the exact action and documents the source of permission.
- Treat `manual_only`, `disabled`, and unknown policies as hard blocks.
- Proposal submission defaults to human action. API submission requires a second explicit feature flag and a per-action confirmation token.
- Direct outreach must be targeted, relevant, rate-limited, auditable, and approved before sending.

## Product principles

- Deterministic rules before LLM calls.
- Structured model output validated with Pydantic/JSON Schema.
- Every proposal claim must map to an evidence record.
- Idempotent ingestion and jobs.
- Provider-neutral interfaces for LLMs, embeddings, notifications, and sources.
- Local-first and private-by-default.
- No hardcoded model names, URLs, secrets, thresholds, or platform behavior.
- Fail closed on policy uncertainty and submission uncertainty.

## Technical baseline

- Python 3.12 baseline unless a milestone changes it with an ADR.
- FastAPI for the local API and server-rendered dashboard.
- SQLAlchemy 2 + Alembic.
- PostgreSQL + pgvector.
- Redis + Celery for background work and schedules.
- Pydantic settings and schemas.
- pytest, Ruff, mypy, and pre-commit.
- Docker Compose for local services.
- Jinja templates and HTMX/local JavaScript for the MVP; do not introduce React without an ADR.

## Code quality

- Use typed public functions and small modules.
- Use UTC internally and render local time at the UI boundary.
- Use UUIDs for internal entities and stable source fingerprints for deduplication.
- Add database constraints for invariants; do not rely only on application checks.
- All external I/O must have timeouts, retries with jitter, and bounded concurrency.
- Log IDs and outcomes, not secrets or full confidential texts.
- Tests must not call live paid APIs by default.
- Recorded fixtures must be scrubbed of personal data and credentials.

## Required project records

Maintain these as the project develops:

- `IMPLEMENTATION_STATUS.md`
- `CHANGELOG.md`
- `docs/adr/` for architectural decisions
- `.env.example`
- `config/*.example.yaml`
- database migrations
- test fixtures and evaluation datasets

## Definition of complete for any milestone

A milestone is complete only when:

- its deliverables exist;
- listed tests pass;
- documentation matches actual behavior;
- security and policy checks pass;
- no unresolved blocker is hidden;
- the user can reproduce the result from a clean checkout.
