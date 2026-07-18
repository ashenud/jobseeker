---
name: jobseeker-milestone
description: Execute or resume one Jobseeker recovery milestone with Docker-only implementation, acceptance-to-test planning, named subagents, evidence receipts, independent review, clean-checkout reproduction, status transitions, and stop-on-failure. Use for numbered prompts or milestones 00-22, full autonomous milestone runs, blocked-milestone recovery, and milestone completion audits in this repository.
---

# Jobseeker milestone runner

## Select the milestone

1. Read `AGENTS.md`, `IMPLEMENTATION_STATUS.md`,
   `docs/milestones/00-index.md`, and `docs/DEMO_ACCEPTANCE.md` completely.
2. Select only the sole `READY` milestone, or resume the sole `IN_PROGRESS`/
   `BLOCKED` milestone named by the user. Never skip an unmet dependency.
3. Read the complete matching milestone, prompt, required patterns, references,
   ADRs, and prior evidence. Treat existing scaffold code as unverified.
4. Set `READY` to `IN_PROGRESS` before implementation edits. Do not clear a
   `BLOCKED` state until the recorded blocker has actually changed.

## Plan with independent context

1. Dispatch `milestone-planner` read-only to map each acceptance item to an
   observable behavior, test/endpoint, exact Docker command, and evidence field.
2. Dispatch `repository-explorer` for relevant runtime/dependency traces when the
   legacy path is unclear.
3. As coordinator, publish the integrated plan, expected files, migrations/API
   changes, policy/security risks, live-integration needs, and stop conditions.
4. Reject plans that accept fixtures for a required live integration, private
   method calls for an HTTP/browser requirement, static success output, zero-test
   commands, or hand-written evidence.

## Implement the vertical slice

1. Assign `milestone-worker` one explicit non-overlapping file set at a time.
   Keep status, policies, evidence, commits, ADR acceptance, and release metadata
   under coordinator ownership.
2. Implement the smallest real end-to-end path through the production boundary.
   Test doubles belong only in test/fixture paths or explicitly selected offline
   configuration.
3. Run all builds, dependencies, Python, migrations, tests, lint, typing,
   evaluation, servers, and workers through Docker Compose. Host commands may
   orchestrate Docker/Git/files/Codex only.
4. Preserve fail-closed platform policy, human submission control, evidence-linked
   claims, idempotency, bounded I/O, secret-free logs, and unrelated user changes.

## Prove acceptance

1. Run milestone-specific Docker gates, the repository fast suite, and all required
   integration/E2E/live-smoke commands. A missing required credential or current
   policy decision is a blocker, never a fake-provider fallback.
2. Create the implementation commit `milestone-NN: implement <capability>`.
3. Reproduce from that commit in a clean checkout or equivalent clean worktree
   with fresh containers/volumes as specified by the milestone.
4. Generate `artifacts/verification/milestone-NN.json` from real results with:

   - milestone, tested commit, UTC time, image digest, and overall result;
   - each command, exit code, duration, and nonzero test count where applicable;
   - each `MNN-ACNN` acceptance result and test/evidence reference;
   - required live-smoke provider/source metadata with secrets and payloads scrubbed;
   - clean-checkout result, placeholder scan, and known limitations.

5. Dispatch `test-evidence-analyst` to validate result-to-acceptance mapping.
6. Dispatch `policy-release-reviewer` independently. Require `GO` with no unresolved
   high/critical finding.
7. Rerun affected gates after fixes. Never accept a reviewer's summary instead of
   coordinator-visible command evidence.

## Complete or stop

On success:

1. Update `IMPLEMENTATION_STATUS.md`, `CHANGELOG.md`, required docs/ADRs, and the
   receipt only after every gate passes.
2. Commit `milestone-NN: record acceptance evidence`.
3. Mark only the next dependency-satisfied milestone `READY` and continue when the
   user requested the full pipeline.

On any failed command, missing evidence, required credential gap, policy
uncertainty, placeholder production path, or reviewer `NO-GO`:

1. Set the milestone `BLOCKED` with the exact command/reason.
2. Preserve logs with secrets scrubbed.
3. Do not update delivery claims, mark `DONE`, commit acceptance, or begin the next
   milestone.
4. Stop the full pipeline and report the blocker honestly.
