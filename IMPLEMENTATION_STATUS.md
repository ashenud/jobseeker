# Implementation status

**Current milestone:** 05 (`IN_PROGRESS`)
**Last completed milestone:** 04
**Overall state:** Milestone 05 architecture, contract, and state-machine recovery
is in progress. Milestone 04 is accepted at implementation commit
`094c2d9981b605ed9e06a2a1c8013dfb858352e6`. Authoritative main and independent
clean-checkout captures passed all 29 Docker gates with 249 full-suite tests and
2 explicit integration tests each. Evidence review passed all ten acceptance
criteria, and policy/release review returned `GO` with no high or critical
findings. The local five-service runtime, real health/readiness API, initial
pgvector migration, and Celery worker/beat foundation are operational.
**Demo readiness:** NO-GO
**Last updated:** 2026-07-25

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
- `BLOCKED`: progress requires user-owned input/credentials/authority or an
  unresolved security, privacy, or compliance decision.
- `DONE`: all deliverables and Docker-only gates passed and were committed.

Only one milestone may be `IN_PROGRESS`. A milestone moves to `DONE` only after a
read-only reviewer independently confirms the evidence artifact and the
coordinating agent reruns the required gates.

## Recovery ledger

| ID | Milestone | Status | Existing assets to revalidate or replace | Acceptance evidence |
|---:|---|---|---|---|
| 00 | Recovery harness and Docker tooling container | DONE | Docker-only harness, fail-closed controls, portable machine evidence, clean reproduction, and independent review accepted | `artifacts/verification/milestone-00.json` (tested commit `b5b45af0e2bcd143cda9e05ef5d36a91351f0b45`) |
| 01 | Project charter and working-demo contract | DONE | Frozen charter, accepted ADRs, executable semantics, fail-closed clean evidence, and independent review | `artifacts/verification/milestone-01.json` (tested commit `522cfbef9f169b4a3add5088e29a3f51941d1bd8`) |
| 02 | Compliance and platform policy registry | DONE | Strict versioned policy schema, pre-I/O denial, bounded confirmation, audit events, CLI, and independent review | `artifacts/verification/milestone-02.json` (tested commit `d410a82e783629297f58c0dd046f459951c35a2d`) |
| 03 | Positioning profile, portfolio inputs, and success metrics | DONE | Strict profile/scoring schemas, scrubbed evidence provenance, typed claim restrictions, executable KPIs, safe CLI, and independent review | `artifacts/verification/milestone-03.json` (tested commit `d40b66f7763fcfb333c77773fc6acb274b69b44c`) |
| 04 | Docker-only development and runtime foundation | DONE | Pinned Docker/Compose runtime, health-aware five-service stack, real FastAPI readiness, pgvector migration, Celery worker/beat, Docker-only scripts, and independent review | `artifacts/verification/milestone-04.json` (tested commit `094c2d9981b605ed9e06a2a1c8013dfb858352e6`) |
| 05 | Architecture, service contracts, and state machines | IN_PROGRESS | Architecture/state docs and enums | Not run |
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
3. If a required command fails, record it, implement the smallest policy-safe
   fix, rerun invalidated gates, and continue. Set `BLOCKED` only for the terminal
   user-input/authority or protected-decision conditions above.
4. Update this file, `CHANGELOG.md`, the prompt ledger, and any ADR only after all
   gates pass.
5. Commit one milestone at a time with `milestone-NN: <outcome>` before making the
   next milestone `READY`.
