# Sequential Codex Prompts

Use this folder to execute milestones as fresh-context Codex phases. Start at prompt `00`, then continue in numeric order through prompt `22`. The agent may update this ledger itself after each prompt passes verification and is committed; no separate user review or input is required between prompts.

## Completion ledger

| Order | Prompt | Milestone document | Status |
|---:|---|---|---|
| 00 | [`00-index.md`](00-index.md) | [`00-index.md`](../milestones/00-index.md) | DONE |
| 01 | [`01-project-charter-and-scope.md`](01-project-charter-and-scope.md) | [`01-project-charter-and-scope.md`](../milestones/01-project-charter-and-scope.md) | DONE |
| 02 | [`02-compliance-and-platform-policy-registry.md`](02-compliance-and-platform-policy-registry.md) | [`02-compliance-and-platform-policy-registry.md`](../milestones/02-compliance-and-platform-policy-registry.md) | TODO |
| 03 | [`03-positioning-profile-and-success-metrics.md`](03-positioning-profile-and-success-metrics.md) | [`03-positioning-profile-and-success-metrics.md`](../milestones/03-positioning-profile-and-success-metrics.md) | TODO |
| 04 | [`04-local-environment-and-repository-bootstrap.md`](04-local-environment-and-repository-bootstrap.md) | [`04-local-environment-and-repository-bootstrap.md`](../milestones/04-local-environment-and-repository-bootstrap.md) | TODO |
| 05 | [`05-architecture-boundaries-and-state-machines.md`](05-architecture-boundaries-and-state-machines.md) | [`05-architecture-boundaries-and-state-machines.md`](../milestones/05-architecture-boundaries-and-state-machines.md) | TODO |
| 06 | [`06-database-schema-and-migrations.md`](06-database-schema-and-migrations.md) | [`06-database-schema-and-migrations.md`](../milestones/06-database-schema-and-migrations.md) | TODO |
| 07 | [`07-source-adapter-framework.md`](07-source-adapter-framework.md) | [`07-source-adapter-framework.md`](../milestones/07-source-adapter-framework.md) | TODO |
| 08 | [`08-initial-compliant-source-integrations.md`](08-initial-compliant-source-integrations.md) | [`08-initial-compliant-source-integrations.md`](../milestones/08-initial-compliant-source-integrations.md) | TODO |
| 09 | [`09-normalization-deduplication-and-rules.md`](09-normalization-deduplication-and-rules.md) | [`09-normalization-deduplication-and-rules.md`](../milestones/09-normalization-deduplication-and-rules.md) | TODO |
| 10 | [`10-llm-gateway-and-structured-scoring.md`](10-llm-gateway-and-structured-scoring.md) | [`10-llm-gateway-and-structured-scoring.md`](../milestones/10-llm-gateway-and-structured-scoring.md) | TODO |
| 11 | [`11-portfolio-knowledge-base-and-retrieval.md`](11-portfolio-knowledge-base-and-retrieval.md) | [`11-portfolio-knowledge-base-and-retrieval.md`](../milestones/11-portfolio-knowledge-base-and-retrieval.md) | TODO |
| 12 | [`12-proposal-generation-and-factuality-guardrails.md`](12-proposal-generation-and-factuality-guardrails.md) | [`12-proposal-generation-and-factuality-guardrails.md`](../milestones/12-proposal-generation-and-factuality-guardrails.md) | TODO |
| 13 | [`13-human-review-dashboard-and-notifications.md`](13-human-review-dashboard-and-notifications.md) | [`13-human-review-dashboard-and-notifications.md`](../milestones/13-human-review-dashboard-and-notifications.md) | TODO |
| 14 | [`14-submission-assistance-and-permitted-connectors.md`](14-submission-assistance-and-permitted-connectors.md) | [`14-submission-assistance-and-permitted-connectors.md`](../milestones/14-submission-assistance-and-permitted-connectors.md) | TODO |
| 15 | [`15-crm-follow-ups-and-feedback-capture.md`](15-crm-follow-ups-and-feedback-capture.md) | [`15-crm-follow-ups-and-feedback-capture.md`](../milestones/15-crm-follow-ups-and-feedback-capture.md) | TODO |
| 16 | [`16-workers-scheduling-idempotency-and-reliability.md`](16-workers-scheduling-idempotency-and-reliability.md) | [`16-workers-scheduling-idempotency-and-reliability.md`](../milestones/16-workers-scheduling-idempotency-and-reliability.md) | TODO |
| 17 | [`17-security-secrets-privacy-and-retention.md`](17-security-secrets-privacy-and-retention.md) | [`17-security-secrets-privacy-and-retention.md`](../milestones/17-security-secrets-privacy-and-retention.md) | TODO |
| 18 | [`18-testing-evaluations-and-quality-gates.md`](18-testing-evaluations-and-quality-gates.md) | [`18-testing-evaluations-and-quality-gates.md`](../milestones/18-testing-evaluations-and-quality-gates.md) | TODO |
| 19 | [`19-observability-cost-controls-and-operations.md`](19-observability-cost-controls-and-operations.md) | [`19-observability-cost-controls-and-operations.md`](../milestones/19-observability-cost-controls-and-operations.md) | TODO |
| 20 | [`20-local-deployment-startup-backup-and-recovery.md`](20-local-deployment-startup-backup-and-recovery.md) | [`20-local-deployment-startup-backup-and-recovery.md`](../milestones/20-local-deployment-startup-backup-and-recovery.md) | TODO |
| 21 | [`21-codex-implementation-workflow-and-release-discipline.md`](21-codex-implementation-workflow-and-release-discipline.md) | [`21-codex-implementation-workflow-and-release-discipline.md`](../milestones/21-codex-implementation-workflow-and-release-discipline.md) | TODO |
| 22 | [`22-pilot-launch-tuning-and-production-readiness.md`](22-pilot-launch-tuning-and-production-readiness.md) | [`22-pilot-launch-tuning-and-production-readiness.md`](../milestones/22-pilot-launch-tuning-and-production-readiness.md) | TODO |

## Operating rules

- Treat each numbered prompt as a fresh gated phase by re-reading that prompt, its milestone document, and required references before edits for that milestone.
- Do not start prompt `NN+1` until prompt `NN` has passed verification, been committed, and this README row is updated by the agent.
- Dispatch sub-agents where helpful for distinct phases such as instruction reading, codebase exploration, planning, disjoint implementation slices, review, record-update preparation, handoff preparation, or test-output analysis. Assign explicit ownership and avoid overlapping writes.
- The prompt itself controls which patterns and supporting docs must be read for that milestone.
- Prefer project-native rules, hooks, and checks over undocumented local state.
- Keep the Docker Compose environment authoritative for database and Redis services.
- Continue through prompt `22` without user review/input gates, but stop at the first unresolved blocker or failing required check; do not skip ahead to later prompts.
