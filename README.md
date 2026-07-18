# Jobseeker - Local Freelance Job Intelligence

Jobseeker is a **local, platform-agnostic freelance job discovery, scoring, proposal-drafting, review, and tracking application** for a senior graphic designer / brand designer / 3D visualizer.

The central rule is deliberate: **automate discovery, normalization, scoring, drafting, notifications, and tracking; require human approval before any external submission unless a platform has an official, explicitly permitted API and the user has enabled it.**

> **Recovery status (2026-07-18):** the previous repository was an unverified
> scaffold, not a working MVP. All milestone completion claims have been reset.
> Start with Milestone 00; do not use the current code as an application demo.
> The required end state is defined in `docs/DEMO_ACCEPTANCE.md`.


## MVP charter summary

The Milestone 01 charter freezes the MVP as a job intelligence and proposal preparation system with a mandatory human approval boundary. The application may ingest permitted opportunities, store raw and normalized records, deduplicate jobs, apply deterministic filters, score remaining jobs, retrieve portfolio evidence, draft truthful proposals, present a review queue, assist manual submission, and track outcomes.

The MVP explicitly does **not** perform automatic marketplace login, CAPTCHA solving, stealth or anti-bot evasion, unattended bulk bidding, automated LinkedIn outreach, forbidden scraping, public SaaS operation, mobile apps, full CRM integrations, or unapproved cold email.

Success for the first production-readiness pilot means the owner can run the app locally for seven consecutive days, ingest permitted jobs from at least three source types, suppress duplicates, reject poor fits deterministically, score and explain remaining jobs, produce evidence-grounded proposal drafts, require owner review before submission, and track outcomes within configured policy, privacy, and cost limits.

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
5. Start Prompt 00. It establishes the Docker tooling container and validators;
   every later application/check command must execute in Docker.
6. For a full run, continue sequentially and stop automatically at the first
   failed gate, policy uncertainty, or required credential gap.

Suggested first Codex instruction:

```text
Use $jobseeker-milestone to execute docs/prompts/00-index.md. Continue through the numbered recovery prompts only after each milestone has passing Docker evidence and an independent GO. Stop at the first blocker and never mark a placeholder or failed gate DONE.
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
        -> manual submit assistance or disabled-by-default permitted API connector
        -> CRM states, follow-ups, metrics, and weekly reports
```

The runtime target is one Windows PC through WSL 2 and Docker Desktop. The API,
database, Redis, workers, scheduler, tests, migrations, and AI/source integration
smokes run in Docker Compose. Runtime LLM, embedding, notification, and source
integrations remain provider-neutral and include deterministic offline test modes,
but the final demo requires bounded real permitted-source and real-AI evidence.

## Operating boundary

This project must never include CAPTCHA bypass, stealth browsing, credential theft, cookie harvesting, anti-bot evasion, proxy rotation intended to evade controls, mass unsolicited messaging, or unapproved auto-bidding. Human approval is mandatory before external communication by default. Platform terms change; missing, unknown, stale, `manual_only`, and `disabled` policy states fail closed, and every connector is disabled until its policy record is reviewed and approved.
