# Milestone 06 - Database Schema and Migrations

## Goal

Create the durable PostgreSQL schema that supports ingestion, evidence-grounded drafting, review history, policy audits, and analytics without storing unnecessary personal data.

## Core tables

### Source and ingestion

- `platforms`
- `source_connections`
- `ingestion_runs`
- `raw_jobs`
- `normalized_jobs`
- `job_skills`
- `job_locations`
- `job_fingerprints`
- `job_duplicates`

### Evaluation and drafting

- `rule_evaluations`
- `score_runs`
- `job_scores`
- `evidence_documents`
- `evidence_chunks`
- `proposal_runs`
- `proposals`
- `proposal_evidence_links`
- `proposal_quality_checks`

### Review and submission

- `review_items`
- `review_decisions`
- `submission_attempts`
- `confirmation_tokens`

### CRM and operations

- `applications`
- `application_events`
- `follow_up_tasks`
- `outcome_feedback`
- `audit_events`
- `llm_usage`

## Canonical normalized job fields

- internal UUID;
- platform ID and external ID;
- canonical URL;
- title, client/company display name;
- raw and cleaned description;
- service categories and skills;
- budget type, currency, min/max, hourly/fixed;
- location/remote eligibility/time-zone constraints;
- posted and first-seen timestamps;
- deadline/expiry when known;
- source trust level;
- language;
- content hash and semantic fingerprint;
- policy version;
- current lifecycle status.

Do not infer unknown budget as zero. Use null plus `budget_known=false`.

## Important constraints

- Unique `(platform_id, external_id)` when external ID exists.
- Unique ingestion idempotency key.
- Proposal revisions are immutable.
- Only one active review item per job/application.
- Confirmation tokens are hashed, single-use, action-scoped, and expire quickly.
- Application events append; current state is derived or transactionally updated.
- Evidence chunks include verification state and allowed-claim classification.

## Indexes

- source/external ID;
- posted time and status;
- content hash;
- trigram or full-text index on title/description;
- vector index only after enough evidence chunks justify it;
- application state and follow-up due time;
- audit correlation ID.

Do not create approximate vector indexes prematurely. Exact search is adequate for a small private portfolio corpus.

## Migration strategy

- Alembic migrations are reviewed, deterministic, and reversible when practical.
- Never use application startup to silently mutate schema.
- Include a seed command for platforms and local development fixtures.
- Back up before destructive migrations.
- Add migration tests from an empty database and from the previous tagged schema.

## Required deliverables

- SQLAlchemy models and repositories.
- Initial Alembic migrations.
- `docs/DATA_MODEL.md` with an ER diagram.
- seed command.
- repository-level integration tests.

## Codex execution prompt

```text
Implement Milestone 06 only. Create the PostgreSQL schema, SQLAlchemy models, repositories, and Alembic migrations described here. Use append-only events and immutable proposal revisions. Add database constraints, seed data, and integration tests. Do not implement connectors or LLM calls.
```

## Verification

```bash
make db-reset
make migrate
make seed
make test-integration
alembic downgrade -1
alembic upgrade head
```

## Acceptance criteria

- [ ] Empty-database migration succeeds.
- [ ] Downgrade/upgrade path is tested where reversible.
- [ ] Duplicate external jobs and duplicate idempotency keys are blocked.
- [ ] Proposal revisions cannot be overwritten.
- [ ] Confirmation tokens are safe and expiring.
- [ ] ER diagram and field definitions match code.
