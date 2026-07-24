# 00 - Codex execution pattern

## Sources of authority

1. `AGENTS.md` defines durable repository rules.
2. `IMPLEMENTATION_STATUS.md` is the only progress ledger.
3. `docs/milestones/00-index.md` defines dependency order and universal gates.
4. The current milestone defines requirements and acceptance.
5. The matching prompt defines task-local scope.
6. `$jobseeker-milestone` defines the repeatable execution procedure.

If these disagree, stop and repair the records before implementation.

## State machine

```text
READY -> IN_PROGRESS -> implementation commit -> Docker gates
      -> independent review -> clean-checkout reproduction
      -> evidence commit -> DONE -> next READY
```

Failed commands, missing evidence, placeholders, infrastructure faults, and
reviewer `NO-GO` findings stay `IN_PROGRESS`: diagnose, implement the smallest
policy-safe fix, rerun invalidated gates, and continue until acceptance passes.
Use `BLOCKED` only for required user-owned input/credentials/authority or an
unresolved security, privacy, or compliance decision.

## Delegation

- Planner/explorer agents are read-only.
- At most one implementation agent edits at a time unless file ownership is
  explicitly disjoint.
- Test and release reviewers do not review their own implementation.
- Only the coordinator updates status, policies, evidence, commits, or release
  records and makes the final gate decision.
- Subagents never submit, message, deploy, rotate secrets, or broaden platform
  permissions.

## Evidence integrity

Generate `artifacts/verification/milestone-NN.json` from real command results. It
must identify the tested commit/image, acceptance IDs, commands, exit codes, test
counts, reviewer verdict, and any required live-smoke metadata. Do not store
secrets, confidential text, full prompts, or raw third-party payloads.

Do not update `DONE`, the changelog delivery section, ADR acceptance, tags, or the
next milestone until the evidence validator passes.
