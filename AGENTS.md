# AGENTS.md - Jobseeker repository rules

## Mission and boundary

Build a reliable local application that discovers permitted freelance design
work, ranks it, drafts evidence-grounded proposals, supports human review and
manual-safe submission, and tracks outcomes. It is not a mass-bidding bot.

Never implement CAPTCHA solving, fingerprint spoofing, stealth/evasion, credential
or cookie capture, forbidden scraping, rate-limit evasion, or unattended bulk
messaging/submission. `manual_only`, `disabled`, unknown, and stale policies are
hard blocks. Real API writes require documented permission, an owner feature flag,
and a single-use per-action confirmation token.

## Required routing

Before every substantial task, read:

1. `IMPLEMENTATION_STATUS.md`
2. `docs/milestones/00-index.md`
3. `docs/DEMO_ACCEPTANCE.md`

For a numbered milestone, invoke `$jobseeker-milestone` and read its complete
milestone, matching prompt, required patterns, supporting references, and relevant
ADRs. `IMPLEMENTATION_STATUS.md` is the only progress ledger.

## Docker-only application workflow

All application builds, dependency resolution, Python commands, migrations,
tests, linters, type checks, evaluations, servers, workers, and release checks run
inside Docker Compose. Host commands may only operate Git, Docker/Compose, files,
Codex control-plane tooling/hooks, or thin wrappers that invoke Docker.

Tests never call live paid services by default. Required live source/AI smokes use
an explicit profile, bounded requests, timeouts, cost/rate limits, scrubbed output,
and supplied secrets. Missing required credentials block the milestone; never
silently fall back to a fake and claim success.

## Milestone pipeline

Run milestones 00-22 sequentially without user review between them when asked to
run the full prompt set. A persistent Codex Goal may track the long run, but never
replaces repository status/evidence.

For each milestone:

1. Verify dependencies are `DONE`; move the sole `READY` item to `IN_PROGRESS`.
2. Plan the smallest operational vertical slice and list expected files/gates.
3. Dispatch named subagents for bounded planning, exploration, disjoint
   implementation, test analysis, compliance review, and release review.
4. Implement real behavior. Stubs, empty adapters, static success responses,
   non-callable shells, and unconditional pass commands do not count.
5. Run the milestone Docker gates plus the repository fast suite.
6. Create the implementation commit and reproduce from that commit/clean checkout.
7. Generate `artifacts/verification/milestone-NN.json` from real results.
8. Obtain an independent read-only `GO`; resolve every blocker and rerun gates.
9. Update status/changelog/ADRs only after acceptance, commit the evidence, make
   the next milestone `READY`, and advance.

At any nonzero command, missing evidence, policy uncertainty, required credential
gap, placeholder, or reviewer `NO-GO`, record the exact blocker, set `BLOCKED`, and
stop the full run. Documenting failure never converts it to a pass.

Only the coordinating agent integrates work, changes policies/status/evidence,
commits, prepares PR/release metadata, and decides final acceptance. Assign one
writer at a time unless subagent file ownership is explicitly non-overlapping.

## Technical baseline

- Python 3.12; FastAPI with Jinja/HTMX/local JavaScript.
- SQLAlchemy 2, Alembic, PostgreSQL, pgvector.
- Redis and Celery worker/beat.
- Pydantic settings/schemas and provider-neutral source/AI/embedding/notification
  interfaces.
- Ruff, mypy, pytest, pre-commit, migration, integration, E2E, evaluation,
  security, and recovery gates.
- UTC internally, UUID internal IDs, stable source fingerprints, database
  constraints, idempotent jobs, bounded external I/O, and secret-free logs.
- No hardcoded provider model, endpoint, secret, threshold, or platform behavior.
- Every proposal claim maps to an eligible evidence record.

Preserve `.env.example`, `config/*.example.yaml`, migrations, scrubbed fixtures,
evaluation datasets, `CHANGELOG.md`, and ADRs as the implementation evolves.
