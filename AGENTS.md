# AGENTS.md - Instructions for Codex

## Mission

Build a reliable local application that helps the owner find suitable freelance design work, rank it, generate truthful tailored proposals, review drafts, and track outcomes. The application is not a mass-bidding bot.

## Mandatory workflow

1. Read `IMPLEMENTATION_STATUS.md` and `docs/milestones/00-index.md` before every substantial task.
2. Run the workflow as an autonomous, sequential milestone pipeline when asked to implement prompts/milestones `00`-`22`; no separate user input or review is required between milestones.
3. Complete each milestone in order: read the complete prompt, milestone document, and required pattern/supporting files; create a brief implementation plan; list expected files; implement the smallest complete vertical slice; run that milestone's checks plus the repository-wide fast suite; update records; commit the milestone; then advance to the next milestone.
4. Dispatch relevant sub-agents for reading, planning, implementation, review, test-analysis, record-update preparation, and milestone handoff work when their scopes are explicit. Sub-agents may work independently within assigned scope; the coordinating agent is accountable for integration, conflict resolution, compliance, final verification, commits, PR metadata, and the final decision that gates passed.
5. Do not skip a dependency or reorder milestones unless the user explicitly authorizes the dependency fix or scope change.
6. Show failures honestly. Do not mark a milestone complete with failing checks. If a milestone is blocked, record the exact blocker and stop the full-workflow run instead of jumping ahead.
7. Update `IMPLEMENTATION_STATUS.md`, the changelog, and architectural decision records only after acceptance criteria pass.

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
