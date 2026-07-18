# Local Freelance Job Agent - Codex Implementation Blueprint

This package is a build-ready documentation set for a **local, platform-agnostic freelance job discovery, scoring, proposal-drafting, review, and tracking agent**.

The central rule is deliberate: **automate discovery, normalization, scoring, drafting, notifications, and tracking; require human approval before any external submission unless a platform has an official, explicitly permitted API and the user has enabled it.**

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

## Default local architecture

```text
Allowed feeds/APIs/manual capture
        -> source adapters
        -> raw job store
        -> normalization + deduplication
        -> deterministic filters
        -> LLM scoring with structured output
        -> portfolio evidence retrieval
        -> proposal draft + factuality gate
        -> local review queue / optional Telegram
        -> user submits manually or enables a permitted official connector
        -> CRM, follow-ups, metrics, and feedback loop
```

## Operating boundary

This project must never include CAPTCHA bypass, stealth browsing, credential theft, cookie harvesting, anti-bot evasion, mass unsolicited messaging, or unapproved auto-bidding. Platform terms change; every connector is disabled until its policy record is reviewed and approved.
