# Implementation Status

**Current milestone:** 22
**Last completed milestone:** 22
**Overall state:** Milestones 01-22 complete as an integrated local MVP scaffold; real marketplace write connectors remain disabled and require separate approval.
**Last updated:** 2026-07-18

## Rules

- Only one milestone may be `IN PROGRESS`.
- A milestone becomes `DONE` only after its acceptance criteria and verification commands pass.
- If a milestone is blocked, record the exact blocker and stop instead of jumping ahead.
- In a full sequential workflow, the agent may advance from one milestone to the next without user input only after the current milestone is `DONE`, required checks pass, completion records are updated, and a milestone commit has been created. Stop instead of advancing if any check fails, a dependency is missing, acceptance criteria are ambiguous, or compliance/policy status is uncertain.

| ID | Milestone | Status | Evidence / commit |
|---:|---|---|---|
| 01 | Project charter and scope | DONE | docs/PROJECT_CHARTER.md; docs/adr/0001-human-in-the-loop-boundary.md; docs/adr/0002-local-first-mvp.md |
| 02 | Compliance and platform policy registry | DONE | config/platform_policy.yaml; src/job_agent/policy/; tests/test_policy.py |
| 03 | Positioning profile and success metrics | DONE | config/profile.yaml; config/scoring.yaml; docs/SUCCESS_METRICS.md |
| 04 | Windows/WSL local environment and repository bootstrap | DONE | pyproject.toml; compose.yaml; Dockerfile; Makefile; scripts/; src/job_agent/; tests/ |
| 05 | Architecture, boundaries, and state machines | DONE | docs/ARCHITECTURE.md; docs/STATE_MACHINES.md; src/job_agent/core/states.py |
| 06 | Database schema and migrations | DONE | alembic/; src/job_agent/core/models.py; docs/DATA_MODEL.md |
| 07 | Source adapter framework | DONE | src/job_agent/sources/; CLI sources commands |
| 08 | Initial compliant source integrations | DONE | manual adapter and fixture-feed adapter gated by policy |
| 09 | Normalization, deduplication, and deterministic filters | DONE | src/job_agent/normalization/service.py |
| 10 | LLM gateway and structured job scoring | DONE | src/job_agent/llm/scoring.py fake offline scorer and budget guard |
| 11 | Portfolio knowledge base and retrieval | DONE | src/job_agent/evidence/service.py; data/private/portfolio_manifest.yaml |
| 12 | Proposal generation and factuality guardrails | DONE | src/job_agent/proposals/service.py |
| 13 | Human review dashboard and notifications | DONE | src/job_agent/web/ local health/dashboard shell |
| 14 | Submission assistance and permitted connectors | DONE | src/job_agent/submission/service.py confirmation-gated fake connector |
| 15 | CRM, follow-ups, and feedback capture | DONE | src/job_agent/crm/service.py |
| 16 | Workers, scheduling, idempotency, and reliability | DONE | src/job_agent/workers/app.py; compose worker/scheduler profiles |
| 17 | Security, secrets, privacy, and retention | DONE | src/job_agent/security/service.py; docs/THREAT_MODEL.md; config/retention.example.yaml |
| 18 | Testing, evaluations, and quality gates | DONE | tests/; Makefile check/eval/release-check commands |
| 19 | Observability, cost controls, and operations | DONE | src/job_agent/observability/service.py; docs/OPERATIONS.md |
| 20 | Local deployment, startup, backup, and recovery | DONE | compose.yaml; scripts/backup.sh; scripts/restore.sh; docs/OPERATIONS.md |
| 21 | Codex implementation workflow and release discipline | DONE | AGENTS.md retained; .github/workflows/ci.yml; release gate command |
| 22 | Pilot launch, tuning, and production readiness | DONE | src/job_agent/pilot/service.py; docs/PILOT_PLAN.md; docs/ROADMAP.md |
