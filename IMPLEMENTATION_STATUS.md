# Implementation status

**Current milestone:** 01 (`IN_PROGRESS`)
**Last completed milestone:** 00
**Overall state:** Milestone 01 ADR lifecycle validation now works from active and
completed ledger states; focused recovery checks pass and the final full evidence
and independent review chain must rerun.
**Demo readiness:** NO-GO
**Last updated:** 2026-07-19

## Why the status was reset

The previous ledger marked milestones 01-22 `DONE`, but the application did not
have an operational FastAPI/ASGI server, SQLAlchemy persistence, working Alembic
migrations, a Celery application, live permitted source reads, a configured AI
gateway, a review UI, or meaningful release and recovery gates. Several commands
returned hard-coded success messages. Those records did not meet the repository's
definition of complete.

Existing files are inputs to the recovery, not acceptance evidence. No milestone
inherits `DONE` from the prior scaffold commit.

## Status values

- `READY`: dependencies are complete and the milestone may start.
- `PENDING`: waiting for earlier dependencies.
- `IN_PROGRESS`: the only milestone currently being implemented.
- `BLOCKED`: a recorded failing gate prevents progress.
- `DONE`: all deliverables and Docker-only gates passed and were committed.

Only one milestone may be `IN_PROGRESS`. A milestone moves to `DONE` only after a
read-only reviewer independently confirms the evidence artifact and the
coordinating agent reruns the required gates.

## Recovery ledger

| ID | Milestone | Status | Existing assets to revalidate or replace | Acceptance evidence |
|---:|---|---|---|---|
| 00 | Recovery harness and Docker tooling container | DONE | Docker-only harness, fail-closed controls, portable machine evidence, clean reproduction, and independent review accepted | `artifacts/verification/milestone-00.json` (tested commit `b5b45af0e2bcd143cda9e05ef5d36a91351f0b45`) |
| 01 | Project charter and working-demo contract | IN_PROGRESS | DONE-state lifecycle test passes; rerun complete main/clean evidence and review | Prior receipt is superseded; no current acceptance receipt |
| 02 | Compliance and platform policy registry | PENDING | Policy models/config/tests | Not run |
| 03 | Positioning profile, portfolio inputs, and success metrics | PENDING | Profile/scoring YAML | Not run |
| 04 | Docker-only development and runtime foundation | PENDING | Dockerfile, Compose, scripts, packaging | Not run |
| 05 | Architecture, service contracts, and state machines | PENDING | Architecture/state docs and enums | Not run |
| 06 | PostgreSQL/pgvector schema, repositories, and migrations | PENDING | Minimal dataclasses/migration must be replaced | Not run |
| 07 | Source adapter framework and ingestion persistence | PENDING | In-memory adapter protocol | Not run |
| 08 | Manual capture and permitted live read integrations | PENDING | Fixture adapters; no live HTTP connector | Not run |
| 09 | Normalization, deduplication, and deterministic filters | PENDING | In-memory rules | Not run |
| 10 | Provider-neutral AI gateway and structured scoring | PENDING | Fake rules scorer | Not run |
| 11 | Portfolio evidence knowledge base and retrieval | PENDING | Minimal manifest/list filter | Not run |
| 12 | Evidence-grounded AI proposal generation | PENDING | Fixed proposal template | Not run |
| 13 | FastAPI/Jinja/HTMX human review application | PENDING | Static non-ASGI shell | Not run |
| 14 | Policy-gated manual submission assistance | PENDING | In-memory package/fake connector | Not run |
| 15 | Persistent CRM, outcomes, and follow-ups | PENDING | In-memory timeline | Not run |
| 16 | Celery workers, schedules, idempotency, and recovery | PENDING | Missing Celery app | Not run |
| 17 | Security, privacy, authentication, and retention | PENDING | Basic string helpers | Not run |
| 18 | Tests, evaluations, and enforceable quality gates | PENDING | Small unit suite and fake release output | Not run |
| 19 | Observability, cost controls, and operations | PENDING | In-memory metrics | Not run |
| 20 | Docker deployment, backup, restore, and clean install | PENDING | Incomplete Compose/plain file archive | Not run |
| 21 | Codex milestone automation and release discipline | PENDING | Recovery workflow created; must be exercised | Not run |
| 22 | Working application demo and shadow-pilot go/no-go | PENDING | Pilot placeholder | Not run |

## Record-update rules

1. Set the next `READY` milestone to `IN_PROGRESS` before implementation edits.
2. Store real verification output under `artifacts/verification/`; do not type a
   success claim by hand.
3. If any required command fails, set the milestone to `BLOCKED`, record the exact
   command and failure, and stop the sequential run.
4. Update this file, `CHANGELOG.md`, the prompt ledger, and any ADR only after all
   gates pass.
5. Commit one milestone at a time with `milestone-NN: <outcome>` before making the
   next milestone `READY`.
