# Milestone 01 - Project Charter and Scope

## Goal

Freeze a realistic MVP so Codex does not build an unsafe or unnecessarily complex “apply everywhere” bot. This milestone converts the broad idea into explicit product boundaries, user stories, non-goals, and success conditions.

## Key decision

The product is a **job intelligence and proposal preparation system with human approval**. It is not a stealth scraper, browser bot, spam engine, or universal auto-apply service.

## Required deliverables

Create:

- `docs/PROJECT_CHARTER.md`
- `docs/adr/0001-human-in-the-loop-boundary.md`
- `docs/adr/0002-local-first-mvp.md`
- an updated `README.md` architecture summary
- a first entry in `CHANGELOG.md`

## Scope to approve

### MVP capabilities

1. Ingest jobs from allowed APIs, RSS/JSON feeds, email/manual copy, and user-provided URLs/text.
2. Store raw source payloads and normalized job records.
3. Deduplicate cross-posted and repeatedly fetched jobs.
4. Apply deterministic filters for service relevance, budget, geography, recency, and banned categories.
5. Use an LLM only after deterministic filtering.
6. Score fit and explain the score with structured output.
7. Retrieve verified portfolio evidence.
8. Draft a short, human-sounding proposal without invented claims.
9. Present a review queue with edit, approve, skip, and reason capture.
10. Assist submission by opening the source page and copying text; optional official API actions remain disabled by default.
11. Track application state and follow-up reminders.
12. Produce weekly performance reports.

### Non-goals for MVP

- Automatic login to marketplaces.
- CAPTCHA solving or anti-bot evasion.
- Unattended bulk bidding.
- Automated LinkedIn connection requests or messaging.
- Scraping a platform that forbids it.
- Replacing the user’s judgment on price, claims, portfolio attachment, or client risk.
- A public multi-tenant SaaS.
- Mobile apps.
- Full CRM integrations.
- Sending cold email without approval.

## Primary user stories

- As the owner, I can see only jobs relevant to packaging, branding, Amazon creative, 3D product visualization, architectural visualization, and production design.
- As the owner, I can understand why a job scored highly or poorly.
- As the owner, I can see which portfolio projects support a proposal’s claims.
- As the owner, I can edit and approve a proposal in under two minutes.
- As the owner, I can prevent any platform from being contacted automatically.
- As the owner, I can see what produced interviews and wins.

## Constraints

- Runs on one Windows PC through WSL 2 and Docker Desktop.
- Must survive restarts without duplicating jobs or proposals.
- Must work without paid LLM calls in development and degraded mode.
- Initial UI is local-only.
- All externally visible actions are auditable.
- Platform policy is configuration plus code enforcement, not a note in documentation.

## Decisions to document

1. Human approval is a hard product boundary.
2. Local-first is the initial deployment target.
3. The runtime is provider-neutral even though Codex builds it.
4. The owner’s portfolio and proposal style are private source data.
5. The app prioritizes quality and account safety over maximum application volume.

## Codex execution prompt

```text
Implement Milestone 01 only. Read AGENTS.md and docs/milestones/01-project-charter-and-scope.md. Create the charter and two ADRs, update README and CHANGELOG, and do not create application code yet. Highlight any scope ambiguity instead of silently deciding it. Finish with the milestone acceptance checklist.
```

## Acceptance criteria

- [ ] The charter contains MVP, non-goals, user stories, constraints, risks, and measurable success criteria.
- [ ] Human approval is defined as mandatory before external communication by default.
- [ ] Local-first and provider-neutral decisions are recorded as ADRs.
- [ ] The scope explicitly prohibits bypass and stealth techniques.
- [ ] The owner can read the charter and decide what the product will and will not do.

## Stop condition

Do not start environment setup or code until the user approves the charter. Scope drift here multiplies every later cost.
