# Milestone 22 - Pilot Launch, Tuning, and Production Readiness

## Goal

Run a controlled real-world pilot, measure quality and risk, tune from evidence, and decide whether the local agent is ready for daily use.

## Pilot phases

### Phase 1 - Shadow mode, 3 days

- Ingest permitted sources.
- Normalize, filter, score, and draft.
- No submissions from the system.
- User labels relevance and proposal quality.
- Compare discovered jobs with normal manual search.

### Phase 2 - Assisted applications, 7 days

- User reviews and manually submits approved packages.
- Track time saved, edits, responses, and errors.
- Limit volume, for example 3-5 high-quality applications per day.
- No real API write connector.

### Phase 3 - Stable daily operation, 14 days

- Enable schedules and notifications.
- Keep submission manual.
- Monitor source staleness, costs, queue age, and false positives.
- Review weekly report and policy status.

Only consider an official write connector after the manual workflow is stable and the benefit clearly exceeds account risk.

## Baseline and targets

Before tuning, record:

- current manual search time/day;
- applications/week;
- reply/interview/win rates if known;
- average time to draft proposal;
- common job categories and budgets.

Pilot go/no-go targets:

- zero unauthorized actions;
- zero unsupported proposal claims;
- at least 80% relevance among surfaced review jobs;
- at least 60% drafts requiring light edits only;
- median review time under two minutes;
- cost within configured ceiling;
- no source repeatedly stale without alert;
- backup and restore proven.

## Tuning order

1. Fix false positives with deterministic rules.
2. Fix false negatives by taxonomy/threshold changes.
3. Improve evidence metadata/retrieval.
4. Adjust scoring prompt.
5. Adjust proposal prompt/style.
6. Change model only after cheaper controls are exhausted.

Never tune solely to maximize applications. Optimize qualified conversations and wins per unit of time/cost.

## Production readiness review

- platform policy current;
- account and data security reviewed;
- source adapters healthy;
- disaster recovery tested;
- evaluation thresholds passing;
- operating costs understood;
- manual workflow comfortable;
- known limitations documented;
- rollback path available.

## Post-pilot roadmap candidates

- email alert importer;
- local browser extension for user-initiated capture;
- improved portfolio attachment recommendation;
- local model fallback;
- approved Freelancer API read connector;
- self-hosted VPS migration after local stability;
- direct-outreach research queue with strict approval;
- optional n8n integration only where it reduces maintenance.

## Required deliverables

- pilot plan and daily checklist;
- baseline report;
- phase reports;
- tuning decisions as ADRs/config changes;
- final go/no-go report;
- prioritized roadmap.

## Codex execution prompt

```text
Implement Milestone 22 only. Add pilot-mode configuration, shadow/assisted/stable phase controls, daily pilot reports, baseline and go/no-go templates, and a production-readiness command. Do not enable real marketplace submission APIs. Produce the final operational checklist and roadmap.
```

## Acceptance criteria

- [ ] Shadow and assisted modes are distinguishable and enforced.
- [ ] Pilot metrics are captured from actual user decisions.
- [ ] Tuning changes are versioned and reversible.
- [ ] Go/no-go decision is evidence-based.
- [ ] Real write connectors remain disabled unless separately approved after pilot.
- [ ] Final system can be operated and recovered by following documentation alone.
