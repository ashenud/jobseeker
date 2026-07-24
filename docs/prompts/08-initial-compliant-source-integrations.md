# Prompt 08 - Initial Compliant Source Integrations

## Execution order

Run this prompt as fresh context step **08**. After this prompt is complete, committed, continue to the next prompt sequentially.

## Required repository skill

Invoke `$jobseeker-milestone` and follow its state transitions, evidence schema, independent-review gate, repair loops, and terminal blocker conditions. The numbered prompt supplies scope; the skill supplies the authoritative execution procedure.

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

The milestone cannot pass with fixture adapters alone. Run mocked connector tests
and the separately enabled bounded live-read profile for two currently permitted
sources. Record endpoint, policy version, response status, item count, and a hash
of the scrubbed fixture; never record credentials or full third-party payloads.

Dependencies recorded in the master index: **07**.

## Instructions

1. Confirm the current branch and repository status before editing.
2. Read the full milestone document and every required pattern file yourself.
3. Present a concise plan, expected files to change, risks, and verification commands before edits.
4. Run every application build, dependency, Python, migration, test, lint, type-check, evaluation, server, and worker command inside Docker Compose. Host commands may only orchestrate Docker, Git, files, and Codex controls.
5. Use `milestone-planner` and `repository-explorer` for read-only planning; `milestone-worker` for one explicitly owned write slice at a time; and independent `test-evidence-analyst` plus `policy-release-reviewer` before acceptance. The coordinator alone integrates, changes records, commits, and decides gates.
6. Use hooks/project rules only when they are repository-native, documented, and do not depend on private local state.
7. Implement the smallest complete vertical slice that satisfies the milestone acceptance criteria.
8. Run the milestone acceptance matrix, required Docker integration or live smoke, repository fast suite, and clean-checkout reproduction. Generate `artifacts/verification/milestone-08.json` from the real results.
9. Treat nonzero commands, missing evidence, placeholders, infrastructure faults, and reviewer `NO-GO` findings as repair-loop inputs: diagnose, implement the policy-safe fix, rerun invalidated gates, and continue. Set `BLOCKED` only when progress requires user-owned input/credentials/authority or an unresolved security, privacy, or compliance decision.
10. If checks pass, update required project records, commit with `milestone-08: <result>`, and continue to the next prompt sequentially unless this is prompt 22.

## Verification checklist

- [ ] Milestone deliverables exist.
- [ ] Pattern files listed above were followed.
- [ ] All application and verification commands ran inside Docker Compose; no host toolchain command was used.
- [ ] Policy/compliance guardrails still fail closed.
- [ ] Every required Docker command passed; documenting a failure never counts as acceptance.
- [ ] `artifacts/verification/milestone-08.json` identifies the tested commit, commands, exit codes, test counts, acceptance IDs, and reviewer verdict.
- [ ] `IMPLEMENTATION_STATUS.md` accurately reflects the milestone state.
- [ ] Final response cites changed files and prefixes every check command with ✅, ⚠️, or ❌.
