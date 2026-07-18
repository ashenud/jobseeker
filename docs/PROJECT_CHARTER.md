# Project Charter

## Product boundary

Jobseeker is a local-first job intelligence and proposal preparation system for freelance design work. It helps the owner discover suitable opportunities, rank them, draft truthful proposals, review drafts, and track outcomes. It is not a stealth scraper, browser bot, spam engine, or unattended auto-apply service.

Human approval is mandatory by default before any externally visible communication, submission, direct outreach, follow-up, or account-affecting action. Official API write actions are out of the MVP default path and may only become available when a platform policy record explicitly permits the exact action, a connector-specific feature flag is enabled, and the user confirms the individual action.

## MVP capabilities

1. Ingest jobs from allowed APIs, RSS or JSON feeds, email/manual copy, and user-provided URLs or text.
2. Store raw source payloads and normalized job records.
3. Deduplicate cross-posted and repeatedly fetched jobs.
4. Apply deterministic filters for service relevance, budget, geography, recency, and banned categories before any LLM call.
5. Use an LLM only after deterministic filtering and only through provider-neutral interfaces with cost controls and a no-paid-LLM development mode.
6. Score fit and explain the score with structured, validated output.
7. Retrieve verified portfolio evidence before drafting claims.
8. Draft short, human-sounding proposals without invented claims.
9. Present a local review queue with edit, approve, skip, and reason capture.
10. Assist manual submission by opening the source page and copying approved text.
11. Keep optional official API submission connectors disabled by default and guarded by policy, feature flags, and per-action confirmation.
12. Track application state, outcomes, follow-up reminders, and weekly performance reports.

## Non-goals for the MVP

- Automatic login to marketplaces.
- CAPTCHA solving, fingerprint spoofing, stealth plugins, hidden browser automation, or proxy rotation intended to evade controls.
- Unattended bulk bidding or mass auto-apply behavior.
- Automated LinkedIn connection requests or messaging.
- Scraping or automating a platform that forbids the exact action.
- Replacing the owner’s judgment on price, claims, portfolio attachment, client risk, or final submission.
- Public multi-tenant SaaS operation.
- Mobile applications.
- Full CRM integrations.
- Sending cold email or other direct outreach without approval.

## Primary user stories

- As the owner, I can see only jobs relevant to packaging, labels, brand identity, Amazon listing images and A+ content, print production, 3D product visualization, architectural visualization, dielines, and mockups.
- As the owner, I can understand why a job scored highly or poorly.
- As the owner, I can see which portfolio projects support each proposal claim.
- As the owner, I can edit and approve a proposal in under two minutes.
- As the owner, I can prevent any platform from being contacted automatically.
- As the owner, I can see which sources, job types, proposals, and follow-ups produced interviews and wins.

## Constraints

- Runs on one Windows PC through WSL 2 and Docker Desktop.
- Initial UI is local-only and private by default.
- Must survive restarts without duplicating jobs, proposals, approvals, or follow-up reminders.
- Must work in development without paid LLM calls.
- All externally visible actions are auditable with action IDs, timestamps, user decisions, and outcomes.
- Platform policy is enforced by configuration and code, not merely documented.
- Unknown, missing, stale, `manual_only`, or `disabled` platform policies fail closed.
- Secrets, platform passwords, cookies, browser session tokens, payment details, and full inbox exports are never stored.
- Owner portfolio data, proposal style, and private notes are treated as private source data.

## Success criteria

The MVP is successful when, from a clean local checkout, the owner can run the system locally for a seven-day pilot and demonstrate that it:

- ingests permitted opportunities from at least three source types;
- suppresses duplicate jobs across repeated ingestion runs;
- rejects clearly unsuitable jobs with deterministic rules before LLM scoring;
- creates structured fit scores and explanations for remaining jobs;
- drafts proposals whose claims map to evidence records;
- keeps every proposal in a human review queue until the owner approves, skips, or edits it;
- assists manual submission without contacting platforms automatically;
- records outcomes and follow-up reminders; and
- stays within configured policy, privacy, and cost limits.

Operational success will be measured by weekly counts of ingested jobs, filtered jobs, reviewed proposals, approved proposals, submissions, interviews, wins, skipped reasons, unsupported-claim blocks, policy blocks, duplicate suppressions, and estimated LLM cost.

## Key risks and controls

| Risk | Control |
|---|---|
| Marketplace account restriction | Manual-first workflow, fail-closed policy registry, no stealth automation, audited write boundary. |
| Proposal hallucination | Evidence retrieval, claim ledger, structured validation, unsupported-claim blocker. |
| Source terms changing | Policy review dates, stale policy alerts, disabled-by-default connectors. |
| Duplicate submission | Separate approval and submission states, idempotency keys, submission receipts. |
| LLM cost runaway | Deterministic filtering first, daily budgets, no-paid-LLM development mode. |
| Private data leak | Local-only default UI, secret exclusion, retention rules, redacted logs. |
| Prompt injection | Treat job text as untrusted data, structured prompts, validators, adversarial tests. |
| PC sleep or offline periods | Local limitation documented, stale source warnings, startup health checks in later milestones. |

## Scope ambiguities requiring owner approval before later milestones

- Exact source list for the first pilot and each source’s permitted actions.
- Minimum acceptable budget thresholds by service type and geography.
- The private portfolio evidence set and which claims the system may use.
- Whether any official write connector should be considered after the manual MVP is stable.
