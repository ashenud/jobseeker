# Prompt 01 - Project Charter And Scope

## Execution order

Run this prompt as fresh context step **01**. After this prompt is complete, committed, continue to the next prompt sequentially.

## Required repository skill

Invoke `$jobseeker-milestone` and follow its state transitions, evidence schema, independent-review gate, and stop conditions. The numbered prompt supplies scope; the skill supplies the authoritative execution procedure.

## Required context to read first

- `AGENTS.md`
- `IMPLEMENTATION_STATUS.md`
- `docs/milestones/00-index.md`
- `docs/milestones/01-project-charter-and-scope.md`

## Required pattern files

- `docs/patterns/00-codex-execution.md`
- `docs/patterns/06-policy-compliance.md`
- `docs/patterns/09-testing-quality-gates.md`

## Supporting references

- `docs/96-risk-register.md`
- `docs/98-source-guideline-page-notes.md`

## Objective

Implement only milestone **01**: Frozen MVP boundary and constraints.

Dependencies recorded in the master index: **None**.

## Instructions

1. Confirm the current branch and repository status before editing.
2. Read the full milestone document and every required pattern file yourself.
3. Present a concise plan, expected files to change, risks, and verification commands before edits.
4. Run every application build, dependency, Python, migration, test, lint, type-check, evaluation, server, and worker command inside Docker Compose. Host commands may only orchestrate Docker, Git, files, and Codex controls.
5. Use `milestone-planner` and `repository-explorer` for read-only planning; `milestone-worker` for one explicitly owned write slice at a time; and independent `test-evidence-analyst` plus `policy-release-reviewer` before acceptance. The coordinator alone integrates, changes records, commits, and decides gates.
6. Use hooks/project rules only when they are repository-native, documented, and do not depend on private local state.
7. Implement the smallest complete vertical slice that satisfies the milestone acceptance criteria.
8. Run the milestone acceptance matrix, required Docker integration or live smoke, repository fast suite, and clean-checkout reproduction. Generate `artifacts/verification/milestone-01.json` from the real results.
9. Any nonzero command, missing required credential, policy uncertainty, placeholder in a required path, missing evidence, or reviewer `NO-GO` sets the milestone to `BLOCKED` and stops the full pipeline.
10. If checks pass, update required project records, commit with `milestone-01: <result>`, and continue to the next prompt sequentially unless this is prompt 22.

## Verification checklist

- [ ] Milestone deliverables exist.
- [ ] Pattern files listed above were followed.
- [ ] All application and verification commands ran inside Docker Compose; no host toolchain command was used.
- [ ] Policy/compliance guardrails still fail closed.
- [ ] Every required Docker command passed; documenting a failure never counts as acceptance.
- [ ] `artifacts/verification/milestone-01.json` identifies the tested commit, commands, exit codes, test counts, acceptance IDs, and reviewer verdict.
- [ ] `IMPLEMENTATION_STATUS.md` accurately reflects the milestone state.
- [ ] Final response cites changed files and prefixes every check command with ✅, ⚠️, or ❌.
