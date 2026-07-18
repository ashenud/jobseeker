# 98 - Source Guideline Page Notes

The attached `reference/freelance_ai_agent_plan.pdf` is the conceptual starting point.

## Page 1

Defines the core reality check: most marketplaces do not support fully autonomous bidding safely. It recommends “AI does most of the work, human approves/sends,” defines scope and positioning, and compares platform automation feasibility.

## Page 2

Recommends a platform-agnostic engine fed by official APIs, RSS/public feeds, and human-approved semi-automatic workflows for restrictive platforms.

## Page 3

Shows the main architecture: job sources, ingestion worker, LLM scoring/filtering, proposal generation with retrieval, human review queue, submission layer, and CRM. It also starts the detailed steps for ingestion, scoring, RAG, and approval UI.

## Page 4

Completes submission, CRM/follow-up, and 24/7 deployment. The current blueprint modifies deployment to **local first**, while retaining a later VPS option.

## Page 5

Lists the original tool direction: Python, an LLM API, Docker Compose, PostgreSQL/pgvector, Redis/Celery, HTTP/RSS ingestion, Playwright only for permitted uses, Telegram or web dashboard, optional n8n, outreach service, and monitoring. It also begins the six-week build order.

## Page 6

Completes the six-week order: approval/submission, CRM/follow-up, deployment/monitoring/tuning.

## Changes made by this blueprint

- Uses ChatGPT Codex as the development workflow.
- Separates Codex from the runtime LLM API.
- Adds a fail-closed platform policy registry.
- Chooses a local Windows/WSL/Docker MVP.
- Adds data contracts, state machines, prompt injection defenses, claim verification, tests/evaluations, cost controls, backups, and release discipline.
- Defaults Behance and restrictive platforms to manual capture/submission.
- Defers all real write connectors until after a stable pilot and explicit permission review.
