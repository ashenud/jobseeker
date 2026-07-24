# Jobseeker - Local Freelance Job Intelligence

Jobseeker is a **local, platform-agnostic freelance job discovery, scoring, proposal-drafting, review, and tracking application** for a senior graphic designer / brand designer / 3D visualizer.

The central rule is deliberate: **automate permitted discovery, normalization,
scoring, drafting, notifications, and tracking; keep transmission manual in the
MVP demo. Approval never transmits—it only prepares reviewed content for the
owner to copy/open and submit manually.**

> **Recovery status:** follow `IMPLEMENTATION_STATUS.md`, the only progress
> ledger. Existing later-milestone application code remains unverified until its
> owning milestone passes Docker evidence and independent review. The required
> end state is defined in `docs/DEMO_ACCEPTANCE.md`.


## MVP charter summary

The Milestone 01 charter freezes the MVP as a job intelligence and proposal
preparation system. The application may ingest permitted opportunities, store and
deduplicate records, filter and score jobs, retrieve portfolio evidence, draft
truthful proposals, present a review queue, prepare a manual submission package,
and track outcomes. Approval, package preparation, manual owner submission, and
the recorded outcome are distinct states; no official write connector is part of
the MVP demo.

Manual capture is required. Jobicy RSS/API and Remote OK JSON/RSS are conditional
read goals, and OpenAI Responses API structured output is a conditional opt-in AI
goal. Naming them grants no permission, credential, spend, endpoint, model, or
write authority; Milestones 02, 08, and 10 are authoritative.

The MVP explicitly does **not** perform automatic marketplace login, CAPTCHA solving, stealth or anti-bot evasion, unattended bulk bidding, automated LinkedIn outreach, forbidden scraping, public SaaS operation, mobile apps, full CRM integrations, or unapproved cold email.

Success requires zero duplicate normalized jobs after repeat ingestion, zero
unsupported proposal claims, zero unapproved external actions, and zero
transmissions caused by approval, alongside persisted review, audit, restart, and
backup/restore evidence.

## What is included

- `AGENTS.md` - permanent project instructions for ChatGPT Codex.
- `IMPLEMENTATION_STATUS.md` - the one source of truth for milestone progress.
- `docs/README.md` - canonical documentation map.
- `docs/DEMO_ACCEPTANCE.md` - observable working-application demo contract.
- `docs/milestones/00-index.md` - recovery sequence, dependencies, and universal gates.
- `docs/milestones/01-...22-...` - authoritative requirements and acceptance.
- `docs/90-...99-...` - supporting references, schemas, prompts, glossary, and research notes.
- `docs/patterns/` - coding standards and implementation patterns that must be read by milestone prompts.
- `docs/prompts/` - ordered task entry prompts; progress is tracked only in `IMPLEMENTATION_STATUS.md`.
- `.agents/skills/jobseeker-milestone/` - reusable gated milestone workflow.
- `.codex/` - named subagents, Docker-boundary hooks, and destructive-command rules.
- `config/*.example.yaml` - non-secret configuration examples.
- `.env.example` - environment variable template.
- `reference/freelance_ai_agent_plan.pdf` - the supplied guideline document.

## Important distinction

**Codex is the software-development agent used to build this repository.** The finished job agent needs its own runtime LLM provider, such as the OpenAI API or a local model. A ChatGPT subscription and API billing are separate products, so the runtime must support a no-LLM/manual mode and enforce a daily cost ceiling.

## Recovery execution

1. Install and enable Docker Desktop/Engine with Docker Compose and WSL integration.
2. Open Codex in this trusted repository so project agents, skills, hooks, and rules load.
3. Review/trust the project hooks with `/hooks` and confirm roles with `/subagents`.
4. Read `AGENTS.md`, `IMPLEMENTATION_STATUS.md`, `docs/milestones/00-index.md`, and `docs/DEMO_ACCEPTANCE.md`.
5. Select only the sole `READY` or `IN_PROGRESS` prompt named by
   `IMPLEMENTATION_STATUS.md`; never infer progress from scaffold files.
6. Continue sequentially only after the current milestone has Docker evidence and
   independent `GO`; stop automatically at the first
   failed gate, policy uncertainty, or required credential gap.

Suggested first Codex instruction:

```text
Use $jobseeker-milestone to execute the sole READY or IN_PROGRESS prompt in IMPLEMENTATION_STATUS.md. Continue only after passing Docker evidence and an independent GO. Stop at the first blocker and never mark a placeholder or failed gate DONE.
```

## Approved local architecture

```text
Permitted APIs / RSS / JSON / manual capture / user-provided text
        -> policy-checked source adapters
        -> raw source payload store
        -> normalized job records
        -> deduplication and deterministic filters
        -> provider-neutral LLM scoring with structured output
        -> private portfolio evidence retrieval
        -> proposal draft with factuality guardrails
        -> local human review queue
        -> locked copy/open/manual-submit package
        -> owner submits manually and records the reference
        -> CRM states, follow-ups, metrics, and weekly reports
```

The runtime target is one Windows PC through WSL 2 and Docker Desktop. The API,
database, Redis, workers, scheduler, tests, migrations, and AI/source integration
smokes run in Docker Compose. Runtime LLM, embedding, notification, and source
integrations remain provider-neutral and include deterministic offline test modes,
but the final demo requires bounded real permitted-source and real-AI evidence.

All application builds, dependency resolution, Python commands, migrations,
tests, linters, type checks, evaluations, servers, workers, schedulers, release
checks, backups, and restores run inside Docker containers. The host is limited to
Git, Docker/Compose orchestration, read-only file inspection, Codex controls, and
thin wrappers that invoke Docker Compose.

## Local runtime foundation

With Docker Engine/Desktop and Docker Compose available, copy `.env.example` to
`.env` only when overrides are needed. The example is safe to use unchanged for
the local stack; source, AI, outreach, browser-fill, and API-write features remain
disabled.

```bash
make bootstrap
make up
make migrate
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
curl http://127.0.0.1:8000/version
make check
make down
```

The API is the only published service and binds to `127.0.0.1`. PostgreSQL and
Redis are reachable only on the Compose network. `make logs`, `make test`,
`make lint`, and `make typecheck` are Docker Compose wrappers; no host Python
environment is used.

## Operating boundary

This project must never include CAPTCHA bypass, stealth browsing, credential
theft, cookie harvesting, anti-bot evasion, proxy rotation intended to evade
controls, mass unsolicited messaging, or unapproved auto-bidding. Approval never
causes external communication. Platform terms change; missing, unknown, stale,
`manual_only`, and `disabled` policy states fail closed before I/O. A future write
proposal remains outside the MVP and would require current permission for the
exact action, an owner feature flag, a single-use per-action confirmation token,
and an audit record containing the action ID, policy decision, timestamp,
destination, checksum, and outcome.
