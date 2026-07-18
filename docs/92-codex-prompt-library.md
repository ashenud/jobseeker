# 92 - Codex Prompt Library

## Start a milestone

```text
Use $jobseeker-milestone to execute the sole READY milestone. Run all application and verification commands inside Docker Compose. Produce acceptance-to-test mappings, real command evidence, independent review, and clean-checkout reproduction. Stop at the first failure or missing required credential; do not hide failures, weaken tests, or mark a placeholder DONE.
```

## Ask for a self-review

```text
As an independent read-only reviewer, review Milestone XX's diff and evidence. Focus on policy bypass, accidental external writes, secrets, PII, prompt injection, SQL/data integrity, idempotency, retries, migration safety, unsupported proposal claims, Docker-only reproduction, placeholder paths, and missing tests. Return GO or NO-GO with cited findings. Do not edit or approve work you implemented.
```

## Debug a failure

```text
Investigate this failure without changing unrelated behavior. Reproduce it inside Docker, identify root cause and the affected invariant, add a failing regression test first, implement the smallest fix, run focused and full Docker suites, and explain why the fix cannot create duplicate external actions or data loss.
```

## Update a platform policy

```text
Do not enable a connector yet. Review the current official terms/API documentation supplied by me for PLATFORM and ACTION. Update the audit record with date, allowed operations, limits, retention/attribution requirements, and uncertainties. Show the proposed policy diff and risks for my approval before changing an action from disabled/manual_only.
```

## Prepare a release

```text
Run the Docker release-readiness process without tagging or deploying. Verify status/evidence, clean-checkout reproduction, image digests, tests, type checks, migrations, browser E2E, live integration receipts, evaluation thresholds, unsupported-claim count, policy dates, security scans, encrypted backup/restore, and changelog. Produce GO or NO-GO with exact failures. Do not bypass a gate.
```
