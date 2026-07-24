# Prompt 17 - Security Secrets Privacy And Retention

## Execution order

Run this prompt as fresh context step **17**. After this prompt is complete, committed, continue to the next prompt sequentially.

## Required repository skill

Invoke `$jobseeker-milestone` and follow its state transitions, evidence schema, independent-review gate, repair loops, and terminal blocker conditions. The numbered prompt supplies scope; the skill supplies the authoritative execution procedure.

## Required context to read first

- `AGENTS.md`
- `IMPLEMENTATION_STATUS.md`
- `docs/milestones/00-index.md`
- `docs/milestones/17-security-secrets-privacy-and-retention.md`

## Required pattern files

- `docs/patterns/00-codex-execution.md`
- `docs/patterns/01-docker-local-environment.md`
- `docs/patterns/05-configuration-secrets.md`
- `docs/patterns/06-policy-compliance.md`
- `docs/patterns/09-testing-quality-gates.md`
- `docs/patterns/10-observability-operations.md`

## Supporting references

- `docs/91-configuration-reference.md`
- `docs/96-risk-register.md`

## Objective

Implement only milestone **17**: Threat model and enforceable data protections.

Dependencies recorded in the master index: **02,04-16**.

## Instructions

1. Confirm the current branch and repository status before editing.
2. Read the full milestone document and every required pattern file yourself.
3. Present a concise plan, expected files to change, risks, and verification commands before edits.
4. Run every application build, dependency, Python, migration, test, lint, type-check, evaluation, server, and worker command inside Docker Compose. Host commands may only orchestrate Docker, Git, files, and Codex controls.
5. Use `milestone-planner` and `repository-explorer` for read-only planning; `milestone-worker` for one explicitly owned write slice at a time; and independent `test-evidence-analyst` plus `policy-release-reviewer` before acceptance. The coordinator alone integrates, changes records, commits, and decides gates.
6. Use hooks/project rules only when they are repository-native, documented, and do not depend on private local state.
7. Implement the smallest complete vertical slice that satisfies the milestone acceptance criteria.
8. Run the milestone acceptance matrix, required Docker integration or live smoke, repository fast suite, and clean-checkout reproduction. Generate `artifacts/verification/milestone-17.json` from the real results.
9. Treat nonzero commands, missing evidence, placeholders, infrastructure faults, and reviewer `NO-GO` findings as repair-loop inputs: diagnose, implement the policy-safe fix, rerun invalidated gates, and continue. Set `BLOCKED` only when progress requires user-owned input/credentials/authority or an unresolved security, privacy, or compliance decision.
10. If checks pass, update required project records, commit with `milestone-17: <result>`, and continue to the next prompt sequentially unless this is prompt 22.

## Verification checklist

- [ ] Milestone deliverables exist.
- [ ] Pattern files listed above were followed.
- [ ] All application and verification commands ran inside Docker Compose; no host toolchain command was used.
- [ ] Policy/compliance guardrails still fail closed.
- [ ] Every required Docker command passed; documenting a failure never counts as acceptance.
- [ ] `artifacts/verification/milestone-17.json` identifies the tested commit, commands, exit codes, test counts, acceptance IDs, and reviewer verdict.
- [ ] `IMPLEMENTATION_STATUS.md` accurately reflects the milestone state.
- [ ] Final response cites changed files and prefixes every check command with ✅, ⚠️, or ❌.
