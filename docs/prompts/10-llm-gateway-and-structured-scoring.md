# Prompt 10 - Llm Gateway And Structured Scoring

## Execution order

Run this prompt as fresh context step **10**. Do not run a later prompt until this prompt is complete, committed, and the prompt index is marked done by a human reviewer.

## Required context to read first

- `AGENTS.md`
- `IMPLEMENTATION_STATUS.md`
- `docs/milestones/00-index.md`
- `docs/milestones/10-llm-gateway-and-structured-scoring.md`

## Required pattern files

- `docs/patterns/00-codex-execution.md`
- `docs/patterns/05-configuration-secrets.md`
- `docs/patterns/08-llm-and-retrieval.md`
- `docs/patterns/09-testing-quality-gates.md`
- `docs/patterns/10-observability-operations.md`

## Supporting references

- `docs/90-data-contracts-and-json-schemas.md`
- `docs/91-configuration-reference.md`
- `docs/94-test-and-evaluation-dataset-guide.md`

## Objective

Implement only milestone **10**: Validated, explainable, budget-controlled scores.

Dependencies recorded in the master index: **03,09**.

## Instructions

1. Confirm the current branch and repository status before editing.
2. Read the full milestone document and every required pattern file yourself.
3. Present a concise plan, expected files to change, risks, and verification commands before edits.
4. Keep Docker as the local runtime boundary when adding runnable services; database and Redis services belong in Docker Compose.
5. Use sub-agents only for optional read-only review or test-output analysis if available in the current Codex session; do not delegate instruction-reading or final decisions.
6. Use hooks/project rules only when they are repository-native, documented, and do not depend on private local state.
7. Implement the smallest complete vertical slice that satisfies the milestone acceptance criteria.
8. Run the milestone checks and repository-wide fast checks.
9. If checks fail, report blockers honestly and do not mark the milestone done.
10. If checks pass, update required project records, commit with `milestone-10: <result>`, and stop before starting the next prompt.

## Verification checklist

- [ ] Milestone deliverables exist.
- [ ] Pattern files listed above were followed.
- [ ] Docker-local assumptions are preserved where relevant.
- [ ] Policy/compliance guardrails still fail closed.
- [ ] Tests and static checks pass or failures are explicitly documented.
- [ ] `IMPLEMENTATION_STATUS.md` accurately reflects the milestone state.
- [ ] Final response cites changed files and prefixes every check command with ✅, ⚠️, or ❌.
