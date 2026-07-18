# 92 - Codex Prompt Library

## Start a milestone

```text
Read AGENTS.md, IMPLEMENTATION_STATUS.md, docs/milestones/00-index.md, and docs/milestones/XX-name.md. Read only the supporting documents linked by that milestone. Work only on Milestone XX. First show a concise plan, expected file changes, risks, and verification commands. Wait for my approval if the plan changes architecture or scope. Then implement, run all checks, and finish with: changed files, commands/results, acceptance checklist, unresolved issues, and next milestone readiness. Do not hide failures or weaken tests.
```

## Ask for a self-review

```text
Review your Milestone XX changes as a strict senior engineer. Focus on policy bypass, accidental external writes, secrets, PII, prompt injection, SQL/data integrity, idempotency, retries, migration safety, unsupported proposal claims, and missing tests. Cite files and lines. Fix confirmed issues, rerun checks, and report remaining risks.
```

## Debug a failure

```text
Investigate this failure without changing unrelated behavior. Reproduce it, identify root cause and affected invariant, add a failing regression test first, implement the smallest fix, run the focused and full fast test suites, and explain why the fix cannot create duplicate external actions or data loss.
```

## Update a platform policy

```text
Do not enable a connector yet. Review the current official terms/API documentation supplied by me for PLATFORM and ACTION. Update the audit record with date, allowed operations, limits, retention/attribution requirements, and uncertainties. Show the proposed policy diff and risks for my approval before changing an action from disabled/manual_only.
```

## Prepare a release

```text
Run the release readiness process without tagging or deploying yet. Verify status, clean Git state, tests, type checks, migrations, evaluation thresholds, unsupported-claim count, policy review dates, security checks, backup/restore evidence, and changelog. Produce a go/no-go report with exact failures. Do not bypass a gate.
```
