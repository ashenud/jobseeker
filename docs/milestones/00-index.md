# 00 - Recovery master index and execution order

## Purpose

This is the authoritative implementation sequence for turning the current
scaffold into a reproducible Docker-only working application demo. Prior `DONE`
labels are void. Existing code may be kept only when the milestone that owns it
proves the current acceptance criteria.

Read this index with `IMPLEMENTATION_STATUS.md`, `docs/DEMO_ACCEPTANCE.md`, and
the current numbered milestone.

## Non-negotiable boundaries

- The product automates permitted discovery and application preparation, not
  uncontrolled bidding.
- Human approval and human action remain the default external-communication
  boundary.
- A marketplace write connector requires current documented API permission, an
  owner-enabled feature flag, and a single-use confirmation token. It is not
  required for the working demo.
- Unknown, stale, `manual_only`, or `disabled` policies fail closed before an
  HTTP or browser action.
- All application builds, dependencies, tests, migrations, servers, workers,
  evaluations, and release checks run inside Docker containers.
- A fake provider is required for deterministic tests but cannot satisfy a
  milestone that explicitly requires an opt-in live API or AI integration smoke.

## Recovery sequence

| ID | Document | Required operational outcome | Depends on |
|---:|---|---|---|
| 00 | This recovery index plus [Prompt 00](../prompts/00-index.md) | Canonical docs, Codex controls, validators, and a buildable Docker tooling container | None |
| 01 | [Project charter and scope](01-project-charter-and-scope.md) | Revalidated charter plus observable working-demo contract | 00 |
| 02 | [Compliance and policy registry](02-compliance-and-platform-policy-registry.md) | Versioned action policy blocks disallowed I/O before connector calls | 01 |
| 03 | [Profile and success metrics](03-positioning-profile-and-success-metrics.md) | Validated owner profile, evidence inputs, demo fixtures, executable KPIs | 01 |
| 04 | [Docker-only foundation](04-local-environment-and-repository-bootstrap.md) | Buildable API/worker/scheduler/Postgres/Redis stack and containerized toolchain | 01-03 |
| 05 | [Architecture and state machines](05-architecture-boundaries-and-state-machines.md) | Real service, transaction, API, audit, and state contracts | 04 |
| 06 | [Database and migrations](06-database-schema-and-migrations.md) | Complete SQLAlchemy/PostgreSQL/pgvector schema and repositories | 05 |
| 07 | [Source framework](07-source-adapter-framework.md) | Policy-checked, persistent, idempotent adapter framework and manual import | 02,05,06 |
| 08 | [Permitted source integrations](08-initial-compliant-source-integrations.md) | Manual capture plus at least two operational policy-approved read sources | 07 |
| 09 | [Normalization and deterministic rules](09-normalization-deduplication-and-rules.md) | Persistent normalization, duplicate handling, and pre-AI rejection | 06-08 |
| 10 | [AI gateway and scoring](10-llm-gateway-and-structured-scoring.md) | Provider-neutral structured scoring with real opt-in AI smoke | 03,09 |
| 11 | [Portfolio knowledge base](11-portfolio-knowledge-base-and-retrieval.md) | Versioned evidence store and inspectable hybrid retrieval | 03,06,10 |
| 12 | [Proposal generation](12-proposal-generation-and-factuality-guardrails.md) | AI drafts with a validated claim-to-evidence ledger | 10,11 |
| 13 | [Human review application](13-human-review-dashboard-and-notifications.md) | Functional FastAPI/Jinja/HTMX review/edit/approve/skip browser flow | 06,12 |
| 14 | [Submission assistance](14-submission-assistance-and-permitted-connectors.md) | Locked manual package, copy/open assistance, and persistent receipt | 02,13 |
| 15 | [CRM and follow-ups](15-crm-follow-ups-and-feedback-capture.md) | Persistent outcomes, audit timeline, reminder drafts, and reports | 06,13,14 |
| 16 | [Workers and reliability](16-workers-scheduling-idempotency-and-reliability.md) | Real Celery queues/beat, atomic cursors, retry bounds, reconciliation | 08-15 |
| 17 | [Security and privacy](17-security-secrets-privacy-and-retention.md) | Web security, secret handling, retention, deletion, and scan gates | 02,04-16 |
| 18 | [Testing and evaluation](18-testing-evaluations-and-quality-gates.md) | Honest unit/integration/E2E/eval/release gates that fail on regressions | 07-17 |
| 19 | [Observability and cost controls](19-observability-cost-controls-and-operations.md) | Dependency-aware health, metrics, budgets, alerts, and runbooks | 16-18 |
| 20 | [Docker deployment and recovery](20-local-deployment-startup-backup-and-recovery.md) | One-command clean install plus encrypted PostgreSQL backup/restore | 17-19 |
| 21 | [Codex and release discipline](21-codex-implementation-workflow-and-release-discipline.md) | Exercised skill, agents, hooks, evidence checker, and release handoff | 01-20 |
| 22 | [Working demo and pilot handoff](22-pilot-launch-tuning-and-production-readiness.md) | Fresh-volume, live-read, real-AI, browser-driven demo and go/no-go | 01-21 |

## Demonstrable checkpoints

| After | Demo capability |
|---:|---|
| 04 | Healthy Docker stack and container-only checks |
| 08 | Jobs persist from manual capture and permitted read APIs |
| 10 | Persisted, schema-valid scoring from fake and opt-in real AI providers |
| 12 | Evidence-grounded proposal generated with zero unsupported claims |
| 13 | Owner reviews and edits a proposal in the browser |
| 16 | Scheduled ingestion and processing survive duplicate delivery/restart |
| 20 | Clean checkout starts and restores from an encrypted backup |
| 22 | Complete working application demo is reproducible |

## Milestone execution protocol

1. Select only the `READY` milestone from `IMPLEMENTATION_STATUS.md` and set it
   to `IN_PROGRESS`.
2. Invoke `$jobseeker-milestone`; read the milestone, its prompt, required
   patterns, and supporting references completely.
3. Use the named read-only planner agent to produce the vertical-slice plan,
   expected files, database/API changes, risks, and exact Docker commands.
4. Dispatch implementation agents only for explicit non-overlapping files. The
   coordinator owns integration and every write that affects status, policies,
   migrations, releases, or commits.
5. Implement the smallest operational slice. Stubs, unconditional success
   printers, empty interfaces, and tests that bypass the real runtime do not count.
6. Run milestone-specific Docker gates and the repository fast suite. Required
   opt-in API/AI smoke tests must actually run; missing credentials make that
   milestone `BLOCKED` rather than `DONE`.
7. Generate `artifacts/verification/milestone-NN.json` from command results.
8. Ask separate read-only quality and compliance agents to inspect the diff and
   evidence. Resolve every high/critical finding.
9. Re-run the gates as coordinator. Update records only after they pass.
10. Commit `milestone-NN: <outcome>`, mark the milestone `DONE`, make only the
    next dependency-satisfied milestone `READY`, and continue. Stop at the first
    blocker or failed gate.

## Universal acceptance gate

Every milestone must prove all applicable items:

- deliverables exist and are integrated through the real application boundary;
- new data is persistent and protected by database constraints where applicable;
- unit and integration tests exercise behavior, not private fake shells;
- `docker compose config` resolves and relevant containers are healthy;
- Ruff, mypy, pytest, migration checks, and policy/security checks pass in Docker;
- docs describe actual commands and actual behavior;
- secrets and personal/confidential data are absent from commits and logs;
- the evidence receipt contains real nonzero test counts and command exit codes;
- a read-only reviewer reports `GO` with no unresolved blocker;
- a clean checkout can reproduce the milestone result.

## Supporting documents

- [Working demo contract](../DEMO_ACCEPTANCE.md)
- [Data contracts and JSON schemas](../90-data-contracts-and-json-schemas.md)
- [Configuration reference](../91-configuration-reference.md)
- [Prompt library](../92-codex-prompt-library.md)
- [Platform connector checklists](../93-platform-connector-checklists.md)
- [Test and evaluation dataset guide](../94-test-and-evaluation-dataset-guide.md)
- [Operations runbooks](../95-operations-runbooks.md)
- [Risk register](../96-risk-register.md)
- [Glossary](../97-glossary.md)
- [Source guideline notes](../98-source-guideline-page-notes.md)
- [Official reference links](../99-official-reference-links.md)
- [Implementation patterns](../patterns/README.md)
- [Prompt ledger](../prompts/README.md)
