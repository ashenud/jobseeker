# Milestone 15 - CRM, Follow-ups, and Feedback Capture

## Goal

Track the application lifecycle and turn outcomes into better filtering and proposals without sending unauthorized follow-ups.

## Application states

- prepared;
- submitted;
- viewed/acknowledged when known;
- replied;
- interview;
- proposal requested/revision;
- won;
- lost;
- withdrawn;
- no response;
- archived.

Use append-only events. The user can correct state with a reason.

## Follow-up policy

Default examples, configurable by platform:

- no response after five days -> create a follow-up draft task;
- interview promised response date missed -> reminder next business day;
- won -> create onboarding checklist;
- lost -> capture reason and lessons;
- platform discourages follow-up -> reminder only, no draft/send.

The system drafts; the user approves and sends. Email send integration is outside MVP unless explicitly enabled and audited.

## Feedback capture

At key points ask for small structured feedback:

- Was the job actually relevant?
- Was the score too high/low?
- Which proposal lines were edited?
- Why was it skipped?
- What caused reply/win/loss?
- Was price, portfolio, timing, or trust the decisive factor?

Do not automatically “learn” by changing prompts in production. Produce suggested threshold/prompt changes for review.

## Analytics

By platform, service, budget band, geography, and proposal style:

- jobs discovered;
- qualified/reviewed/submitted;
- reply/interview/win rate;
- median response time;
- average project value when won;
- top skip and loss reasons;
- score calibration;
- portfolio evidence associated with success.

Avoid vanity metrics. A source with many jobs and no replies is not performing.

## Required deliverables

- CRM views and application event service;
- follow-up scheduler and draft task creation;
- feedback forms;
- weekly report generator;
- CSV/JSON export;
- tests for state and due-date logic.

## Codex execution prompt

```text
Implement Milestone 15 only. Add append-only application events, CRM views, configurable follow-up tasks that create drafts/reminders but never send, outcome feedback, and a weekly funnel report. Add tests for business-day dates, state corrections, and metric formulas.
```

## Acceptance criteria

- [ ] Every application state change is auditable.
- [ ] Follow-ups are tasks/drafts, not unattended messages.
- [ ] User corrections preserve history.
- [ ] Funnel metrics have documented formulas.
- [ ] Data exports exclude secrets and can be deleted.
- [ ] Feedback can identify false-positive scoring and proposal edits.
