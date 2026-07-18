# Prompt 02 - Compliance And Platform Policy Registry

## Execution order

Run this prompt as fresh context step **02**. Do not run a later prompt until this prompt is complete, committed, and the prompt index is marked done by a human reviewer.

## Required context to read first

- `AGENTS.md`
- `IMPLEMENTATION_STATUS.md`
- `docs/milestones/00-index.md`
- `docs/milestones/02-compliance-and-platform-policy-registry.md`

## Required pattern files

- `docs/patterns/00-codex-execution.md`
- `docs/patterns/05-configuration-secrets.md`
- `docs/patterns/06-policy-compliance.md`
- `docs/patterns/09-testing-quality-gates.md`

## Supporting references

- `docs/91-configuration-reference.md`
- `docs/93-platform-connector-checklists.md`
- `docs/96-risk-register.md`
- `docs/99-official-reference-links.md`

## Objective

Implement only milestone **02**: Every platform/action has an enforceable policy mode.

Dependencies recorded in the master index: **01**.

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
10. If checks pass, update required project records, commit with `milestone-02: <result>`, and stop before starting the next prompt.

## Verification checklist

- [ ] Milestone deliverables exist.
- [ ] Pattern files listed above were followed.
- [ ] Docker-local assumptions are preserved where relevant.
- [ ] Policy/compliance guardrails still fail closed.
- [ ] Tests and static checks pass or failures are explicitly documented.
- [ ] `IMPLEMENTATION_STATUS.md` accurately reflects the milestone state.
- [ ] Final response cites changed files and prefixes every check command with ✅, ⚠️, or ❌.
