# Prompt 08 - Initial Compliant Source Integrations

## Execution order

Run this prompt as fresh context step **08**. After this prompt is complete, committed, and the prompt index is marked done by the agent, continue to the next prompt sequentially.

## Required context to read first

- `AGENTS.md`
- `IMPLEMENTATION_STATUS.md`
- `docs/milestones/00-index.md`
- `docs/milestones/08-initial-compliant-source-integrations.md`

## Required pattern files

- `docs/patterns/00-codex-execution.md`
- `docs/patterns/01-docker-local-environment.md`
- `docs/patterns/05-configuration-secrets.md`
- `docs/patterns/06-policy-compliance.md`
- `docs/patterns/07-background-jobs.md`
- `docs/patterns/09-testing-quality-gates.md`

## Supporting references

- `docs/93-platform-connector-checklists.md`
- `docs/94-test-and-evaluation-dataset-guide.md`
- `docs/99-official-reference-links.md`

## Objective

Implement only milestone **08**: Manual import + two public feeds + optional official API.

Dependencies recorded in the master index: **07**.

## Instructions

1. Confirm the current branch and repository status before editing.
2. Read the full milestone document and every required pattern file yourself.
3. Present a concise plan, expected files to change, risks, and verification commands before edits.
4. Keep Docker as the local runtime boundary when adding runnable services; database and Redis services belong in Docker Compose.
5. Dispatch sub-agents for instruction reading, planning support, review, test-output analysis, record-update preparation, handoff preparation, or disjoint implementation slices when useful; the coordinating agent integrates results and enforces final compliance/check decisions.
6. Use hooks/project rules only when they are repository-native, documented, and do not depend on private local state.
7. Implement the smallest complete vertical slice that satisfies the milestone acceptance criteria.
8. Run the milestone checks and repository-wide fast checks.
9. If checks fail, report blockers honestly and do not mark the milestone done.
10. If checks pass, update required project records, commit with `milestone-08: <result>`, update the prompt index, and continue to the next prompt sequentially unless this is prompt 22.

## Verification checklist

- [ ] Milestone deliverables exist.
- [ ] Pattern files listed above were followed.
- [ ] Docker-local assumptions are preserved where relevant.
- [ ] Policy/compliance guardrails still fail closed.
- [ ] Tests and static checks pass or failures are explicitly documented.
- [ ] `IMPLEMENTATION_STATUS.md` accurately reflects the milestone state.
- [ ] Final response cites changed files and prefixes every check command with ✅, ⚠️, or ❌.
