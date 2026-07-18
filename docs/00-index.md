# 00 - Master Index and Execution Order

## Purpose

This index turns the supplied six-page guideline into a local, implementable, platform-agnostic system. The source guideline recommends a human-in-the-loop pipeline: job sources -> ingestion -> scoring -> proposal generation with retrieval -> approval -> submission -> CRM. It also warns that many marketplaces prohibit unattended bidding. This plan preserves that principle and adds implementation contracts, tests, security, local deployment, Codex instructions, and a policy registry.

## Non-negotiable product boundary

The finished product performs **continuous discovery and preparation**, not uncontrolled account automation. Human approval is required at the boundary where the system communicates externally, except where an official API explicitly permits the action and the user has enabled that connector.

## Target owner profile used by the examples

- Senior Graphic Designer / Brand Designer / 3D Visualizer.
- Strong areas: packaging and labels, Amazon listing images and A+ content, brand identity, print production, 3D product visualization, architectural visualization, dielines and mockups.
- Portfolio: `https://www.behance.net/47pixels`.
- Local host: Windows PC with Docker Desktop and WSL 2.

Keep these values in configuration, never hardcoded in proposal code.

## Milestone sequence

| ID | Document | Outcome | Depends on |
|---:|---|---|---|
| 01 | [`01-project-charter-and-scope.md`](01-project-charter-and-scope.md) | Frozen MVP boundary and constraints | None |
| 02 | [`02-compliance-and-platform-policy-registry.md`](02-compliance-and-platform-policy-registry.md) | Every platform/action has an enforceable policy mode | 01 |
| 03 | [`03-positioning-profile-and-success-metrics.md`](03-positioning-profile-and-success-metrics.md) | Machine-readable freelancer profile and KPIs | 01 |
| 04 | [`04-local-environment-and-repository-bootstrap.md`](04-local-environment-and-repository-bootstrap.md) | Reproducible Windows/WSL/Docker development environment | 01-03 |
| 05 | [`05-architecture-boundaries-and-state-machines.md`](05-architecture-boundaries-and-state-machines.md) | Approved component map, interfaces, and state transitions | 01-04 |
| 06 | [`06-database-schema-and-migrations.md`](06-database-schema-and-migrations.md) | Durable normalized data model | 05 |
| 07 | [`07-source-adapter-framework.md`](07-source-adapter-framework.md) | Pluggable compliant ingestion contract | 02,05,06 |
| 08 | [`08-initial-compliant-source-integrations.md`](08-initial-compliant-source-integrations.md) | Manual import + two public feeds + optional official API | 07 |
| 09 | [`09-normalization-deduplication-and-rules.md`](09-normalization-deduplication-and-rules.md) | Clean jobs, duplicates suppressed, cheap filters first | 06-08 |
| 10 | [`10-llm-gateway-and-structured-scoring.md`](10-llm-gateway-and-structured-scoring.md) | Validated, explainable, budget-controlled scores | 03,09 |
| 11 | [`11-portfolio-knowledge-base-and-retrieval.md`](11-portfolio-knowledge-base-and-retrieval.md) | Evidence library and relevant retrieval | 03,06,10 |
| 12 | [`12-proposal-generation-and-factuality-guardrails.md`](12-proposal-generation-and-factuality-guardrails.md) | Truthful proposal drafts with evidence links | 10,11 |
| 13 | [`13-human-review-dashboard-and-notifications.md`](13-human-review-dashboard-and-notifications.md) | Review/edit/approve/skip queue | 06,12 |
| 14 | [`14-submission-assistance-and-permitted-connectors.md`](14-submission-assistance-and-permitted-connectors.md) | Safe copy/open/manual submit and gated API connectors | 02,13 |
| 15 | [`15-crm-follow-ups-and-feedback-capture.md`](15-crm-follow-ups-and-feedback-capture.md) | Outcome tracking and follow-up drafts | 06,13,14 |
| 16 | [`16-workers-scheduling-idempotency-and-reliability.md`](16-workers-scheduling-idempotency-and-reliability.md) | Continuous local operation without duplicate work | 08-15 |
| 17 | [`17-security-secrets-privacy-and-retention.md`](17-security-secrets-privacy-and-retention.md) | Threat model and enforceable data protections | 02,04-16 |
| 18 | [`18-testing-evaluations-and-quality-gates.md`](18-testing-evaluations-and-quality-gates.md) | Repeatable tests and LLM evaluations | 07-17 |
| 19 | [`19-observability-cost-controls-and-operations.md`](19-observability-cost-controls-and-operations.md) | Health, logs, metrics, budgets, runbooks | 16-18 |
| 20 | [`20-local-deployment-startup-backup-and-recovery.md`](20-local-deployment-startup-backup-and-recovery.md) | One-command local deployment and recovery | 17-19 |
| 21 | [`21-codex-implementation-workflow-and-release-discipline.md`](21-codex-implementation-workflow-and-release-discipline.md) | Safe repeatable Codex workflow | All prior docs |
| 22 | [`22-pilot-launch-tuning-and-production-readiness.md`](22-pilot-launch-tuning-and-production-readiness.md) | Controlled real-world pilot and go/no-go decision | 01-21 |

## Supporting documents

- [`90-data-contracts-and-json-schemas.md`](90-data-contracts-and-json-schemas.md)
- [`91-configuration-reference.md`](91-configuration-reference.md)
- [`92-codex-prompt-library.md`](92-codex-prompt-library.md)
- [`93-platform-connector-checklists.md`](93-platform-connector-checklists.md)
- [`94-test-and-evaluation-dataset-guide.md`](94-test-and-evaluation-dataset-guide.md)
- [`95-operations-runbooks.md`](95-operations-runbooks.md)
- [`96-risk-register.md`](96-risk-register.md)
- [`97-glossary.md`](97-glossary.md)
- [`98-source-guideline-page-notes.md`](98-source-guideline-page-notes.md)
- [`99-official-reference-links.md`](99-official-reference-links.md)

## Six-week execution map

| Week | Milestones | Demonstrable result |
|---|---|---|
| 1 | 01-05 | Local repository, policy boundary, architecture, and runnable skeleton |
| 2 | 06-09 | Jobs enter from compliant sources, normalize, dedupe, and filter |
| 3 | 10-12 | Jobs are scored and truthful proposals are drafted from portfolio evidence |
| 4 | 13-14 | User can review, edit, approve, and submit safely |
| 5 | 15-18 | CRM, follow-ups, reliable workers, security, and tests |
| 6 | 19-22 | Monitoring, local deployment, pilot, tuning, and release decision |

## How to execute each milestone with Codex

1. Set the milestone to `IN PROGRESS` in `IMPLEMENTATION_STATUS.md`.
2. Give Codex only the current milestone plus directly referenced supporting documents.
3. Require a plan before edits.
4. Let Codex implement and run checks.
5. Review the diff and application behavior.
6. Complete the acceptance checklist.
7. Commit with `milestone-XX: <result>`.
8. Mark it `DONE`, set the next milestone to `IN PROGRESS`, and continue.

## Final MVP definition

The MVP is successful when it can run locally for seven consecutive days, ingest permitted jobs from at least three source types, deduplicate them, reject poor fits deterministically, score remaining jobs with structured output, draft evidence-grounded proposals, place them in a human review queue, open the original job, copy the approved proposal, record outcomes, schedule follow-ups, and stay within configured cost and policy limits.
