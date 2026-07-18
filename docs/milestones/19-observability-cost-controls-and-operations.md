# Milestone 19 - Observability, Cost Controls, and Operations

## Goal

Make the local agent understandable when it is healthy, slow, costly, stale, or wrong. Silent failure is worse than no automation.

## Structured logs

Include:

- timestamp UTC;
- level;
- service/task;
- correlation ID;
- platform/source;
- job/application ID;
- outcome and duration;
- retry count;
- policy decision/version;
- model/prompt version and token counts when relevant.

Exclude secrets, full proposal text, full raw jobs, and personal contact data by default.

## Metrics

### Pipeline

- source last success and age;
- items fetched/new/duplicate/error;
- jobs by state;
- queue depth and task latency;
- score/draft failures;
- review queue age;
- follow-ups overdue.

### LLM/cost

- calls and tokens by task/model;
- estimated daily/monthly cost;
- cache/reuse rate;
- cost per reviewed/submitted job;
- budget stops.

### Business

- reviewed/submitted/replied/interviewed/won;
- response/win rates;
- score calibration;
- source/service performance.

## Alerts

Local dashboard plus optional notification for:

- source stale beyond threshold;
- worker heartbeat missing;
- queue backlog;
- repeated schema failures;
- policy review expired;
- daily cost threshold reached;
- backup failed;
- disk space low;
- unknown submission result.

Avoid alert spam. Group repeated failures and include an action/runbook link.

## Cost controls

- daily/monthly hard ceilings;
- maximum LLM calls per job;
- cheaper model for scoring and stronger model only when justified;
- deterministic prefilter;
- content length caps;
- embeddings only on changed evidence;
- no automatic multi-variant proposals;
- manual “re-run” with displayed estimated cost.

## Required deliverables

- structured logging and redaction;
- `/metrics` or internal metrics page;
- health dashboard;
- LLM usage ledger and budget service;
- alert provider interface;
- runbook links;
- load/staleness tests.

## Codex execution prompt

```text
Implement Milestone 19 only. Add structured redacted logs, health/business/LLM metrics, hard cost ceilings, source staleness and worker alerts, and runbook-linked failure views. Demonstrate a budget stop and stale-source alert using tests or a local simulation.
```

## Acceptance criteria

- [ ] User can tell whether each source and worker is healthy.
- [ ] Daily/monthly cost cannot exceed configured hard limits.
- [ ] Logs are useful without exposing full sensitive content.
- [ ] Alerts identify action and link to a runbook.
- [ ] Business metrics are separated from system metrics.
- [ ] Unknown submission and backup failure are high-priority alerts.
