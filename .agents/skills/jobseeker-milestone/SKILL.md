---
name: jobseeker-milestone
description: Execute or resume one Jobseeker recovery milestone with Docker-only implementation, acceptance-to-test planning, named subagents, evidence receipts, repair-and-rerun loops, independent review, clean-checkout reproduction, and terminal user/security blockers. Use for numbered prompts or milestones 00-22, full autonomous milestone runs, blocked-milestone recovery, and milestone completion audits in this repository.
---

# Jobseeker milestone runner

## Select the milestone

1. Read `AGENTS.md`, `IMPLEMENTATION_STATUS.md`,
   `docs/milestones/00-index.md`, and `docs/DEMO_ACCEPTANCE.md` completely.
2. Select only the sole `READY` milestone, or resume the sole `IN_PROGRESS`/
   `BLOCKED` milestone named by the user. Never skip an unmet dependency.
3. Read the complete matching milestone, prompt, required patterns, references,
   ADRs, and prior evidence. Treat existing scaffold code as unverified.
4. Set `READY` to `IN_PROGRESS` before implementation edits. Resume `BLOCKED`
   only after the required user-owned input/authority arrives or the protected
   security, privacy, or compliance decision is resolved.

## Plan with independent context

1. Dispatch `milestone-planner` read-only to map each acceptance item to an
   observable behavior, test/endpoint, exact Docker command, and evidence field.
2. Dispatch `repository-explorer` for relevant runtime/dependency traces when the
   legacy path is unclear.
3. As coordinator, publish the integrated plan, expected files, migrations/API
   changes, policy/security risks, live-integration needs, repair loops, and
   terminal blocker conditions.
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
   integration/E2E/live-smoke commands. Repair ordinary failures and rerun them.
   A missing user-owned credential or unresolved protected policy decision is a
   terminal blocker, never a fake-provider fallback.
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

## Complete, repair, or block

On success:

1. Update `IMPLEMENTATION_STATUS.md`, `CHANGELOG.md`, required docs/ADRs, and the
   receipt only after every gate passes.
2. Commit `milestone-NN: record acceptance evidence`.
3. Mark only the next dependency-satisfied milestone `READY` and continue when the
   user requested the full pipeline.

On a recoverable command, test, evidence, placeholder, infrastructure, or
reviewer failure:

1. Keep the milestone `IN_PROGRESS` and preserve scrubbed diagnostics.
2. Identify the probable root cause, implement the smallest policy-safe fix, and
   add or preserve regression coverage.
3. Rerun the failed gate and every required gate invalidated by the change. A
   reviewer `NO-GO` requires fixes, affected gate reruns, and a fresh independent
   review.
4. Repeat the repair-and-rerun loop until the real acceptance command passes.
5. Use exact read-only diagnostics before infrastructure cleanup. Perform
   destructive cleanup only when repository rules and user authority allow the
   resolved targets.
6. Never weaken acceptance, delete a valid regression, bypass policy, substitute
   a fake for a required live integration, hand-write success evidence, or imply
   a pass before a successful rerun.

Set `BLOCKED` and stop only when progress requires user-owned input, a secret or
credential, an owner choice, permission, external authority, or resolution of a
security, privacy, or compliance uncertainty that cannot be decided safely from
repository evidence:

1. Record the exact missing input, authority, or protected decision.
2. Preserve logs with secrets and private content scrubbed.
3. Do not update delivery claims, mark `DONE`, commit acceptance, or begin the
   next milestone.
4. Report the probable root cause and policy-safe possible fixes. Identify the
   preferred fix and why, likely files, risks, and exact Docker commands for
   verification.
5. When the cause is uncertain, distinguish facts from hypotheses and gather
   only read-only diagnostics.
6. Keep actions requiring the missing authority advisory and report the terminal
   blocker honestly.
