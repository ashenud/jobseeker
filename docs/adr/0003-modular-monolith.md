# ADR 0003: Modular monolith

## Status

Accepted

## Context

The local MVP needs FastAPI, Celery workers, PostgreSQL, Redis, source and AI
adapters, review, submission assistance, and CRM. These capabilities have
different responsibilities, but one owner operates them on one workstation.
Independent network services would add deployment, authentication, versioning,
and distributed-transaction failure modes before those costs buy useful
isolation.

The system still needs enforceable boundaries. In particular, workers must not
contain domain rules, approval must not reach a connector, provider selection
must not leak into domain code, and state plus audit must commit atomically.

## Decision

Use one Python distribution as a modular monolith with FastAPI and Celery runtime
entrypoints. Modules communicate through typed application/domain contracts and
provider-neutral protocols. Dependencies point inward: web routes, tasks,
repositories, and providers implement or invoke contracts; domain contracts do
not import FastAPI, Celery, SQLAlchemy, or provider SDKs.

State mutation occurs only through `TransitionCommand` and the transition
application service. That service owns one UoW transaction, canonical edge
validation, and a single repository operation that atomically serializes or
compare-and-swaps expected state, claims the unique idempotency key, and stages
state plus audit. Concrete repository/schema work is deferred to Milestone 06.

Module responsibilities and forbidden duties are maintained in
`docs/ARCHITECTURE.md` and exposed from production metadata at
`GET /api/v1/architecture`.

## Consequences

- One image and repository remain straightforward to run and reproduce locally.
- In-process calls are typed and testable without distributed RPC.
- FastAPI and Celery may scale as separate processes while sharing contracts.
- Discipline and architecture tests, rather than network separation, enforce
  module boundaries.
- A slow or faulty adapter must still use bounded I/O and cannot be isolated by a
  service boundary in this MVP.
- Extracting a module into a service later requires a new ADR and an explicit
  transaction/data ownership design; current protocols offer potential seams but
  do not promise distributed compatibility.
