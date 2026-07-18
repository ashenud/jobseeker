# Milestone 16 - Workers, Scheduling, Idempotency, and Reliability

## Goal

Run ingestion, normalization, scoring, embedding, drafting, follow-up checks, and reports continuously on the local PC without duplicate or runaway work.

## Queue design

Recommended Celery queues:

- `ingestion`;
- `processing`;
- `llm`;
- `notifications`;
- `maintenance`.

Route expensive/slow tasks separately so one source cannot block review activity.

## Task principles

- small, idempotent tasks;
- database-backed status and idempotency keys;
- bounded retries with exponential backoff and jitter;
- explicit hard and soft time limits;
- dead-letter/failure records;
- no infinite chains;
- no external write in a retryable generic task;
- advisory locks or unique constraints for singleton schedules.

## Schedules

- source polling by source configuration;
- stale-job expiry hourly;
- follow-up due scan daily;
- weekly report;
- policy review due check daily;
- retention cleanup daily;
- database backup per local schedule;
- health heartbeat every few minutes.

Add jitter so all sources do not fire at the same second.

## Idempotency examples

- ingestion: hash of platform/source/cursor/time bucket;
- normalize: raw job ID + normalizer version;
- score: normalized job ID + profile/prompt/schema/model version;
- embed: chunk content hash + embedding model;
- proposal: job score ID + evidence set hash + prompt version;
- notification: review item ID + notification type;
- submission: application ID + locked revision + destination.

## Crash recovery

- workers acknowledge after safe persistence;
- tasks stuck past lease timeout are recoverable;
- startup reconciliation scans inconsistent states;
- LLM timeout does not lose the job;
- source cursor advances only after batch commit;
- local power loss leaves an auditable retry path.

## Required deliverables

- Celery app and queue routing;
- schedules from configuration;
- task wrappers and idempotency service;
- failure/dead-letter views;
- reconciliation command;
- resilience tests.

## Codex execution prompt

```text
Implement Milestone 16 only. Connect the existing services through Celery queues and schedules with database idempotency, bounded retries, time limits, circuit breakers, and reconciliation. Add tests for duplicate delivery, worker crash, cursor commit, LLM timeout, and power-loss-style restart. Do not add any unattended external write task.
```

## Acceptance criteria

- [ ] Duplicate task delivery does not duplicate domain records or calls.
- [ ] Cursor commits are atomic with stored results.
- [ ] Failed tasks are visible and recoverable.
- [ ] External write actions are absent from scheduled/retryable tasks.
- [ ] Reconciliation repairs or reports inconsistent states.
- [ ] Seven-day local operation is technically supportable.
