# Sequential Codex prompts

These files are thin entry points for the recovery pipeline. They do not maintain
a second progress ledger. `IMPLEMENTATION_STATUS.md` is the only status source.

Start with Prompt 00 and invoke `$jobseeker-milestone`. Continue automatically in
numeric order only after the current milestone has passing evidence, independent
review, a completion commit, and the next milestone is marked `READY`.

| Order | Prompt | Authoritative milestone |
|---:|---|---|
| 00 | [Recovery orchestration](00-index.md) | [Master index / recovery harness](../milestones/00-index.md) |
| 01 | [Project charter](01-project-charter-and-scope.md) | [Milestone 01](../milestones/01-project-charter-and-scope.md) |
| 02 | [Policy registry](02-compliance-and-platform-policy-registry.md) | [Milestone 02](../milestones/02-compliance-and-platform-policy-registry.md) |
| 03 | [Profile and metrics](03-positioning-profile-and-success-metrics.md) | [Milestone 03](../milestones/03-positioning-profile-and-success-metrics.md) |
| 04 | [Docker foundation](04-local-environment-and-repository-bootstrap.md) | [Milestone 04](../milestones/04-local-environment-and-repository-bootstrap.md) |
| 05 | [Architecture](05-architecture-boundaries-and-state-machines.md) | [Milestone 05](../milestones/05-architecture-boundaries-and-state-machines.md) |
| 06 | [Database](06-database-schema-and-migrations.md) | [Milestone 06](../milestones/06-database-schema-and-migrations.md) |
| 07 | [Source framework](07-source-adapter-framework.md) | [Milestone 07](../milestones/07-source-adapter-framework.md) |
| 08 | [Source integrations](08-initial-compliant-source-integrations.md) | [Milestone 08](../milestones/08-initial-compliant-source-integrations.md) |
| 09 | [Normalization and rules](09-normalization-deduplication-and-rules.md) | [Milestone 09](../milestones/09-normalization-deduplication-and-rules.md) |
| 10 | [AI scoring](10-llm-gateway-and-structured-scoring.md) | [Milestone 10](../milestones/10-llm-gateway-and-structured-scoring.md) |
| 11 | [Evidence retrieval](11-portfolio-knowledge-base-and-retrieval.md) | [Milestone 11](../milestones/11-portfolio-knowledge-base-and-retrieval.md) |
| 12 | [Proposal generation](12-proposal-generation-and-factuality-guardrails.md) | [Milestone 12](../milestones/12-proposal-generation-and-factuality-guardrails.md) |
| 13 | [Review application](13-human-review-dashboard-and-notifications.md) | [Milestone 13](../milestones/13-human-review-dashboard-and-notifications.md) |
| 14 | [Submission assistance](14-submission-assistance-and-permitted-connectors.md) | [Milestone 14](../milestones/14-submission-assistance-and-permitted-connectors.md) |
| 15 | [CRM](15-crm-follow-ups-and-feedback-capture.md) | [Milestone 15](../milestones/15-crm-follow-ups-and-feedback-capture.md) |
| 16 | [Workers](16-workers-scheduling-idempotency-and-reliability.md) | [Milestone 16](../milestones/16-workers-scheduling-idempotency-and-reliability.md) |
| 17 | [Security and privacy](17-security-secrets-privacy-and-retention.md) | [Milestone 17](../milestones/17-security-secrets-privacy-and-retention.md) |
| 18 | [Testing and evaluation](18-testing-evaluations-and-quality-gates.md) | [Milestone 18](../milestones/18-testing-evaluations-and-quality-gates.md) |
| 19 | [Observability](19-observability-cost-controls-and-operations.md) | [Milestone 19](../milestones/19-observability-cost-controls-and-operations.md) |
| 20 | [Deployment and recovery](20-local-deployment-startup-backup-and-recovery.md) | [Milestone 20](../milestones/20-local-deployment-startup-backup-and-recovery.md) |
| 21 | [Codex/release discipline](21-codex-implementation-workflow-and-release-discipline.md) | [Milestone 21](../milestones/21-codex-implementation-workflow-and-release-discipline.md) |
| 22 | [Working demo](22-pilot-launch-tuning-and-production-readiness.md) | [Milestone 22](../milestones/22-pilot-launch-tuning-and-production-readiness.md) |

## Failure rule

Any failed command, missing required credential, policy uncertainty, missing
evidence, placeholder production path, or reviewer `NO-GO` stops the entire run.
Recording a failure is required for honesty but never converts it into a pass.

See [TEMPLATE.md](TEMPLATE.md) for required prompt fields and
[the demo contract](../DEMO_ACCEPTANCE.md) for the final observable outcome.
