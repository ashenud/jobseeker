# Jobseeker - Local Freelance Job Intelligence

Jobseeker is a **local, platform-agnostic freelance job discovery, scoring, proposal-drafting, review, and tracking application** for a senior graphic designer / brand designer / 3D visualizer.

The central rule is deliberate: **automate discovery, normalization, scoring, drafting, notifications, and tracking; require human approval before any external submission unless a platform has an official, explicitly permitted API and the user has enabled it.**


## MVP charter summary

The Milestone 01 charter freezes the MVP as a job intelligence and proposal preparation system with a mandatory human approval boundary. The application may ingest permitted opportunities, store raw and normalized records, deduplicate jobs, apply deterministic filters, score remaining jobs, retrieve portfolio evidence, draft truthful proposals, present a review queue, assist manual submission, and track outcomes.

The MVP explicitly does **not** perform automatic marketplace login, CAPTCHA solving, stealth or anti-bot evasion, unattended bulk bidding, automated LinkedIn outreach, forbidden scraping, public SaaS operation, mobile apps, full CRM integrations, or unapproved cold email.

Success for the first production-readiness pilot means the owner can run the app locally for seven consecutive days, ingest permitted jobs from at least three source types, suppress duplicates, reject poor fits deterministically, score and explain remaining jobs, produce evidence-grounded proposal drafts, require owner review before submission, and track outcomes within configured policy, privacy, and cost limits.

## What is included

- `AGENTS.md` - permanent project instructions for ChatGPT Codex.
- `IMPLEMENTATION_STATUS.md` - the one source of truth for milestone progress.
- `docs/milestones/00-index.md` - master index, sequence, dependencies, and six-week plan.
- `docs/milestones/01-...22-...` - executable milestones in required order.
- `docs/90-...99-...` - supporting references, schemas, prompts, glossary, and research notes.
- `docs/patterns/` - coding standards and implementation patterns that must be read by milestone prompts.
- `docs/prompts/` - ordered fresh-context prompts for automating milestone execution.
- `config/*.example.yaml` - non-secret configuration examples.
- `.env.example` - environment variable template.
- `reference/freelance_ai_agent_plan.pdf` - the supplied guideline document.

## Important distinction

**Codex is the software-development agent used to build this repository.** The finished job agent needs its own runtime LLM provider, such as the OpenAI API or a local model. A ChatGPT subscription and API billing are separate products, so the runtime must support a no-LLM/manual mode and enforce a daily cost ceiling.

## First-time setup

1. Extract this ZIP into a normal project folder.
2. Open the folder in Git and create the first commit.
3. Open Codex in this folder.
4. Ask Codex to read `AGENTS.md`, `IMPLEMENTATION_STATUS.md`, and `docs/milestones/00-index.md`.
5. Open `docs/prompts/README.md` and run the numbered prompts sequentially as fresh Codex contexts.
6. Start only Milestone 01 after prompt `00` has been reviewed and marked complete.

Suggested first Codex instruction:

```text
Read docs/prompts/01-project-charter-and-scope.md in a fresh Codex context and execute it exactly. Do not implement later milestones. Complete Milestone 01 exactly, create or update its required artifacts, run every listed verification step, and show me the acceptance checklist before marking the milestone complete.
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

The runtime target is one Windows PC through WSL 2 and Docker Desktop. Later milestones will keep database, Redis, workers, and service dependencies behind Docker Compose while keeping the initial dashboard local-only. Runtime LLM, embedding, notification, and source integrations must be provider-neutral and support a no-paid-LLM development mode.

## Operating boundary

This project must never include CAPTCHA bypass, stealth browsing, credential theft, cookie harvesting, anti-bot evasion, proxy rotation intended to evade controls, mass unsolicited messaging, or unapproved auto-bidding. Human approval is mandatory before external communication by default. Platform terms change; missing, unknown, stale, `manual_only`, and `disabled` policy states fail closed, and every connector is disabled until its policy record is reviewed and approved.
