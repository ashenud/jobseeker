# Project charter

## Product boundary

Jobseeker is a local-first job intelligence and proposal-preparation application
for permitted freelance design work. It helps the owner capture opportunities,
rank them, draft evidence-grounded proposals, review drafts, prepare a manual
submission package, and track outcomes. It is not a scraper, browser bot, spam
engine, mass-bidding system, or unattended auto-apply service.

Approval and transmission are separate decisions. Approval never transmits a
proposal, message, or follow-up. It only locks reviewed content and prepares a
copy/open/manual-submit package. The owner leaves the application, submits
manually on the source platform, then records the submission reference. The MVP
demo contains no official write connector.

## Ordered user-visible demo flow

This journey specializes the mandatory sequence in `docs/DEMO_ACCEPTANCE.md`:

1. From a clean checkout, the owner supplies documented secrets and starts the
   Docker Compose application through its Docker-only bootstrap wrapper.
2. The owner sees dependency-aware health for the API, worker, scheduler,
   PostgreSQL/pgvector, Redis, migrations, and current platform policies.
3. The owner ingests a scrubbed fixture, uses manual capture for one opportunity,
   and performs one bounded live read only when the current policy permits it.
4. Re-ingesting the same source record produces zero duplicate normalized jobs;
   the owner can inspect the retained source and idempotency result.
5. Deterministic rules reject unsuitable work before AI, while retained work gets
   a schema-valid score with provider, model, prompt, cost, and latency metadata.
6. The application retrieves eligible portfolio evidence and drafts a proposal
   whose factual claims all link to evidence records, with zero unsupported claims.
7. In the local browser, the owner reviews the job, risks, score, evidence, and
   draft; edits it; and sees both revisions retained.
8. The owner approves the reviewed revision. Approval prepares and locks a
   copy/open/manual-submit package; it performs zero external transmissions.
9. The owner copies or opens the package, manually submits on the source platform,
   and returns to record a manual submission reference and outcome.
10. The owner sees the audit timeline and a scheduled follow-up draft; no follow-up
    message is sent by the application.
11. After a stack restart, records persist and duplicate tasks or submissions are
    not created.
12. The owner exports metrics, runs Docker-only release checks, and verifies an
    encrypted PostgreSQL-aware backup and fresh-volume restore.

## MVP capabilities

- Policy-checked fixture and manual capture, normalization, persistence, and
  idempotent deduplication.
- Deterministic filtering before provider-neutral AI scoring.
- Evidence retrieval and claim-to-evidence proposal drafting.
- A local human review queue with immutable revisions and explicit decisions.
- Manual copy/open submission preparation, manual reference capture, CRM events,
  follow-up drafts, metrics, and auditable outcomes.
- Fail-closed workers, retries, budgets, health checks, backup, and recovery.

## Conditional integration goals and authority

The named read goals are **manual capture**, **Jobicy RSS/API**, and
**Remote OK JSON/RSS**. The named AI goal is an opt-in
**OpenAI Responses API structured output** smoke. These names are conditional
evaluation targets, not enabled integrations.

Naming a provider or source grants no permission, credential, spend, endpoint
selection, model selection, scraping authority, or write authorization. Milestone
02 is authoritative for current action-specific policy. Milestone 08 is
authoritative for permitted source implementation and its bounded live read.
Milestone 10 is authoritative for provider-neutral AI configuration and the
opt-in real-AI structured-output smoke. Missing permission, policy freshness,
credentials, budget, endpoint configuration, or model configuration blocks the
applicable milestone rather than selecting or enabling a fallback.

Behance and Upwork remain manual capture and manual owner submission unless a
later current policy explicitly permits a narrower action. No official write
connector is part of the MVP demo. A later write proposal would require separate
scope approval, current documented permission for the exact action, an
owner-enabled feature flag, a single-use per-action confirmation token, and an
audit record containing action ID, policy decision, timestamp, destination,
checksum, and outcome.

## Non-goals

- Automatic marketplace login, bid, proposal submission, messaging, or follow-up.
- CAPTCHA solving, credential or cookie capture, fingerprint spoofing, stealth or
  anti-bot evasion, hidden browser automation, or rate-limit evasion.
- Scraping or automating an action not explicitly permitted by current policy.
- Unattended bulk bidding, mass outreach, or automated LinkedIn messaging.
- A public multi-tenant SaaS, mobile app, or full external CRM integration.
- Invented portfolio facts, unsupported proposal claims, or automatic pricing.
- An official marketplace write connector in the MVP demo.

## User stories

- As the owner, I can see why a permitted job was kept, rejected, or prioritized.
- As the owner, I can trace every proposal claim to eligible evidence.
- As the owner, I can edit and approve a proposal without that approval sending it.
- As the owner, I can manually submit a prepared package and record what happened.
- As the owner, I can verify that no platform action occurred without permission.
- As the owner, I can see which sources and proposals produced interviews or wins.

## Docker-only and local-first constraint

The host may run only Git, Docker/Compose orchestration, read-only file inspection,
Codex control-plane operations, and thin shell wrappers that invoke Docker
Compose. All application builds, dependency resolution, Python commands,
migrations, tests, linters, type checks, evaluations, servers, workers,
schedulers, release checks, backups, and restores run inside Docker containers.
The API, worker, scheduler, PostgreSQL/pgvector, Redis, and browser-facing local
application are Docker Compose services. The dashboard binds locally by default.

The target is one owner-controlled Windows PC using WSL 2 and Docker Desktop.
Private portfolio evidence, notes, proposal revisions, and source material remain
private inputs. A public or multi-tenant deployment requires a separate ADR.

## Measurable success and automatic no-go conditions

The demo passes only when it reports:

- zero duplicate normalized jobs after repeat ingestion;
- zero unsupported proposal claims;
- zero unapproved external actions;
- zero transmissions caused by approval;
- nonzero persisted opportunities, proposal revisions, audit events, and Docker
  test counts; and
- successful restart persistence plus encrypted backup/restore reproduction.

Any required live goal without current policy permission or required credentials,
any unsupported claim, any unapproved action, any host-native application command,
or any failed gate is an automatic no-go.

## Frozen decisions and downstream fail-closed inputs

The following decisions are frozen for the MVP:

1. Submission is manual; approval only prepares a package.
2. Manual capture is always in the demo. Jobicy and Remote OK are conditional read
   candidates whose exact action and endpoint must pass Milestones 02 and 08.
3. OpenAI Responses API structured output is the conditional real-AI smoke goal;
   provider, endpoint, model, credential, and budget remain validated Milestone 10
   inputs and are never hardcoded here.
4. Behance and Upwork use manual capture and manual owner submission.
5. Budget thresholds, private portfolio evidence, and eligible claims are supplied
   and validated in Milestones 03 and 11; missing values block dependent behavior
   and must never be invented.
6. Local-first and Docker-only execution remain mandatory for the MVP.

These are downstream inputs, not open scope questions. A later milestone stops
fail-closed when one is missing, stale, contradictory, or unauthorized.

## Risks and controls

| Risk | Frozen control |
|---|---|
| Marketplace restriction | Manual submission, current action policy, no stealth or auto-write. |
| Unsupported proposal claim | Eligible evidence ledger and a hard review block. |
| Source terms change | Review dates and denial before network I/O. |
| Duplicate submission | Separate approval/submission states, checksums, and receipts. |
| AI cost runaway | Deterministic filtering, explicit opt-in, and hard budgets. |
| Private-data exposure | Local binding, private inputs, retention, and redacted logs. |
| Prompt injection | Untrusted-source isolation, structured schemas, and adversarial tests. |
