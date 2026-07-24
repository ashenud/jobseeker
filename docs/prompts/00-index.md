# Prompt 00 - Master orchestration setup

## Execution order

Run this prompt as fresh context step **00**. After this prompt is complete, committed, continue to the next prompt sequentially.

## Required repository skill

Invoke `$jobseeker-milestone` and follow its state transitions, evidence schema, independent-review gate, repair loops, and terminal blocker conditions. The numbered prompt supplies scope; the skill supplies the authoritative execution procedure.

## Required context to read first

- `AGENTS.md`
- `IMPLEMENTATION_STATUS.md`
- `docs/milestones/00-index.md`
- `docs/DEMO_ACCEPTANCE.md`

## Required pattern files

- `docs/patterns/00-codex-execution.md`
- `docs/patterns/09-testing-quality-gates.md`

## Supporting references

- None beyond the milestone and pattern files.

## Objective

Implement only milestone **00**: establish the recovery harness before application
milestones start.

Dependencies recorded in the master index: **None**.

## Instructions

1. Confirm the current branch and repository status before editing.
2. Read the full milestone document and every required pattern file yourself.
3. Present a concise plan, expected files to change, risks, and verification commands before edits.
4. Run every application build, dependency, Python, migration, test, lint, type-check, evaluation, server, and worker command inside Docker Compose. Host commands may only orchestrate Docker, Git, files, and Codex controls.
5. Use `milestone-planner` and `repository-explorer` for read-only planning; `milestone-worker` for one explicitly owned write slice at a time; and independent `test-evidence-analyst` plus `policy-release-reviewer` before acceptance. The coordinator alone integrates, changes records, commits, and decides gates.
6. Use hooks/project rules only when they are repository-native, documented, and do not depend on private local state.
7. Implement the smallest complete vertical slice that satisfies the milestone acceptance criteria.
8. Run the milestone acceptance matrix, required Docker integration or live smoke, repository fast suite, and clean-checkout reproduction. Generate `artifacts/verification/milestone-00.json` from the real results.
9. Treat nonzero commands, missing evidence, placeholders, infrastructure faults, and reviewer `NO-GO` findings as repair-loop inputs: diagnose, implement the policy-safe fix, rerun invalidated gates, and continue. Set `BLOCKED` only when progress requires user-owned input/credentials/authority or an unresolved security, privacy, or compliance decision.
10. If checks pass, update required project records, commit with `milestone-00: <result>`, and continue to the next prompt sequentially unless this is prompt 22.

## Milestone 00 deliverables

- one canonical milestone tree and one prompt tree;
- reset implementation status and non-duplicated documentation map;
- valid repo-local Codex skill, named agent roles, hooks, and command rules;
- documentation/status/evidence validators;
- a Docker tooling image/service capable of running the validators, Ruff, mypy,
  pytest, and pre-commit without host Python dependencies;
- negative tests proving missing evidence and direct host toolchain commands are
  rejected;
- a successful dry run that leaves Milestone 01 `READY` and does not claim any
  application milestone is complete.

## Required Docker verification

```bash
docker compose --profile dev config --quiet
docker compose --profile dev build api
docker compose --profile dev run --rm --no-deps api python scripts/validate_docs.py
docker compose --profile dev run --rm --no-deps api python scripts/validate_milestone.py --all
docker compose --profile dev run --rm --no-deps api python scripts/validate_codex_controls.py
docker compose --profile dev run --rm --no-deps api ruff check .
docker compose --profile dev run --rm --no-deps api mypy src
docker compose --profile dev run --rm --no-deps api pytest -q
```

If the current Dockerfile/Compose layout cannot run these commands, fixing only
the tooling/container foundation is in scope for Milestone 00. Operational API,
database, worker, and product behavior remain Milestone 04 and later work.

## Verification checklist

- [ ] Milestone deliverables exist.
- [ ] Pattern files listed above were followed.
- [ ] All application and verification commands ran inside Docker Compose; no host toolchain command was used.
- [ ] Policy/compliance guardrails still fail closed.
- [ ] Every required Docker command passed; documenting a failure never counts as acceptance.
- [ ] `artifacts/verification/milestone-00.json` identifies the tested commit, commands, exit codes, test counts, acceptance IDs, and reviewer verdict.
- [ ] `IMPLEMENTATION_STATUS.md` accurately reflects the milestone state.
- [ ] Final response cites changed files and prefixes every check command with ✅, ⚠️, or ❌.
