# Architecture

## Shape and dependency direction

Jobseeker is a local-first modular monolith. FastAPI, Celery, and future
SQLAlchemy adapters live in one Python distribution and share typed inward-facing
contracts. They are separate runtime processes, not separate domain services.

Dependencies point inward:

```text
FastAPI routes ─┐
Celery tasks  ──┼─> application services ─> domain state/contracts
repositories  ──┘              │
provider adapters <──────── provider-neutral protocols
```

Domain and application contracts do not import FastAPI, Celery, SQLAlchemy, a
provider SDK, a model name, an endpoint, or a credential. Transport handlers
validate/serialize and delegate. Workers schedule or retry application-service
commands. Only adapters know concrete transports or persistence.

## Bounded modules

| Module | Responsibility | Forbidden responsibility | May depend on |
|---|---|---|---|
| `core` | State graphs, transition commands, application-service contracts, errors, audit event shape | Provider selection, HTTP, task scheduling, database implementation | Python standard library |
| `policy` | Decide whether an exact action has current authority before I/O | Platform transport, implicit permission, or changing a denial into an allow | `core` |
| `sources` | Retrieve permitted source records and retain raw provenance | Score, draft, submit, or bypass policy | `core`, `policy`, provider contracts |
| `normalization` | Convert raw records to canonical jobs and stable fingerprints | External I/O or provider-specific behavior | `core` |
| `rules` | Apply deterministic eligibility and priority rules | LLM calls or state mutation outside a command | `core` |
| `scoring` | Request and validate structured, provider-neutral scores | Select provider/model or approve a job | `core`, provider contracts |
| `knowledge` | Store eligible evidence and retrieve relevant chunks | Invent evidence or treat restricted evidence as eligible | `core`, provider contracts |
| `proposals` | Generate immutable revisions and validate every claim-to-evidence link | Submit content or edit a locked revision in place | `core`, `knowledge`, provider contracts |
| `review` | Own human edits, rejection, approval, and proposal locking | Treat approval as transmission | `core`, `proposals` |
| `submission` | Prepare manual packages and gate a separately authorized future connector write | Infer permission from approval or run unattended writes | `core`, `policy`, `review`, provider contracts |
| `crm` | Own application outcomes, audit timeline, and follow-up drafts | Rewrite proposal history or send without approval | `core` |
| `workers` | Retry and schedule idempotent application-service commands | Domain decisions or any `SubmissionConnector` dependency in retryable transition tasks | application services only |
| `web` | Expose typed local API operations and server-rendered review screens | Own transactions, domain rules, or provider calls | application services and read models |

Cross-module calls use UUID aggregate identifiers, UTC timestamps, correlation
IDs, and narrow typed request/result objects. Raw third-party payloads and full
proposal text do not cross a boundary unless the receiving use case explicitly
needs them.

## Transactions, repositories, and audit

`TransitionCommand` is the only application-service mutation contract. It
contains the aggregate type and UUID, optimistic `expected_state`, target state,
actor, reason, correlation UUID, and idempotency key. A command cannot mix job,
proposal, and application states.

`TransitionApplicationService` owns the transaction:

1. Open a `UnitOfWork`.
2. Look up the aggregate type and idempotency key.
3. Return the recorded result when the same command is replayed; reject reuse of
   the key for a different command.
4. Read current state and compare it with `expected_state`.
5. Validate the edge using the canonical graph.
6. Stage the state update and `AuditEvent` together.
7. Commit once.

The repository protocol deliberately offers `stage_state_and_audit`, not
independent state and log writes. A concrete repository and database constraints
belong to Milestone 06. A failed validation or conflict commits neither.

Audit events contain only structured identifiers, state names, bounded
single-line actor/reason/idempotency metadata, correlation ID, event ID, and UTC
time. They contain no credentials, authorization headers, cookies, raw payloads,
or full confidential job/proposal text. Likely secret assignments are rejected
before a transaction opens.

## Provider boundaries and external actions

`SourceAdapter`, `LLMProvider`, `EmbeddingProvider`, `EvidenceRetriever`,
`NotificationProvider`, and `SubmissionConnector` are asynchronous,
provider-neutral protocols. Their types select no marketplace, model, endpoint,
credential, or business threshold.

Every external read or write requires a current explicit policy decision before
the adapter is called. Missing, unknown, stale, `manual_only`, or `disabled`
authority fails closed. Approval is never authority for I/O.

A future API submission request must carry all of:

- a current allow decision bound to the exact action and destination;
- an owner-enabled feature flag;
- an unexpired single-use confirmation token bound to application UUID,
  destination, locked proposal checksum, action, and actor.

The connector receives that fully bound request. Package preparation and manual
submission recording remain distinct operations. The MVP has no authorized
official write connector.

## Approval, application ownership, and workers

Proposal approval changes a reviewed proposal revision to `APPROVED`. It does
not call a connector. The next proposal command may lock the immutable revision,
and the application aggregate may then enter `READY_TO_PREPARE`. Application
state owns package preparation, cancellation, manual/API submission recording,
and outcomes.

The job machine contains the documented end-to-end summary states for routing
and queue visibility. The application aggregate is authoritative for package,
submission, and outcome data. A later persisted workflow may project an
application transition to the matching job summary only through one
application-service transaction; callers may not update either state ad hoc.

Retryable workers accept transition commands and call the application service.
Idempotency makes duplicate delivery safe. The retryable transition boundary has
no `SubmissionConnector`, notification, source, or LLM dependency and therefore
cannot turn approval or a retry into external I/O.

## HTTP API and errors

The running FastAPI application exposes:

- `GET /api/v1/architecture`
- `GET /api/v1/state-machines`
- `POST /api/v1/transitions/validate`

Responses are typed and present in OpenAPI. Architecture and graph responses are
derived from production constants. Validation uses the same canonical transition
function as the application service.

Valid edges return HTTP 200 and `valid: true`. An unknown state returns HTTP 400
with `unknown_state`. A forbidden edge or cross-machine attempt returns HTTP 409
with `invalid_transition` or `cross_machine_transition`. Persistence-facing
errors additionally define `state_conflict`, `aggregate_not_found`, and
`idempotency_conflict`. Error bodies contain stable codes and safe state
metadata, never internal exception traces or command payloads.

## Privacy and PII

Only the minimum required data crosses a module boundary. Use internal UUIDs
instead of account identifiers, destination references instead of credentials,
checksums instead of proposal bodies where authorization is evaluated, and
recipient references instead of contact data where possible. Logs and audit
events exclude raw source payloads, prompts, proposals, access tokens, cookies,
and confidential evidence. UI localization is the only place UTC values may be
converted to local time.
