# Working application demo acceptance contract

## Demo outcome

The owner can open a local browser, ingest a real opportunity from a permitted
source or manual paste, persist it, normalize and deduplicate it, score it with a
configured AI provider, generate an evidence-grounded proposal, review and edit
the draft, prepare a manual submission package, and record the outcome. Workers,
PostgreSQL, pgvector, Redis, the API, and the dashboard all run in Docker
containers.

This is an assisted-application demo. It is not permission to scrape, bypass a
platform control, or submit without a human decision.

## Mandatory demo scenario

1. Start from a clean checkout with only Docker Engine/Desktop and Docker Compose
   available on the host.
2. Copy `.env.example` to `.env`, provide a test AI API key through the documented
   secret mechanism, and run the documented Docker-only bootstrap command.
3. Start `api`, `worker`, `scheduler`, `db`, and `redis` containers.
4. Verify liveness, readiness, database migration revision, worker heartbeat, and
   policy-registry freshness.
5. Ingest one scrubbed fixture, one manual job, and one live read from a source
   whose current policy explicitly permits that read.
6. Demonstrate persistence and idempotency by re-ingesting the same source record
   and showing that no duplicate normalized job is created.
7. Show deterministic filtering and a structured AI score with provider, model,
   prompt, schema, cost, and latency metadata.
8. Retrieve verified portfolio evidence and generate a proposal whose factual
   claims all link to evidence records.
9. Review the job in the browser, edit the proposal, preserve both revisions,
   approve it, and create a copy/open/manual-submit package without external
   submission.
10. Record a manual submission reference and CRM outcome; show the audit timeline
    and scheduled follow-up.
11. Restart the stack and prove records survive without duplicate tasks.
12. Export metrics, run the fast/release suites, create a PostgreSQL-aware encrypted
    backup, restore into fresh volumes, and rerun the smoke test.

## Docker-only execution boundary

Application builds, dependency resolution, Python commands, migrations, tests,
linters, type checks, evaluations, development servers, workers, and release
checks must execute inside Docker containers. Host commands are limited to Git,
Docker/Compose orchestration, read-only file inspection, Codex tooling, and the
small shell wrappers that call Docker.

Canonical commands established by Milestone 04 must include:

```bash
docker compose --profile dev build
docker compose --profile dev up -d
docker compose --profile dev run --rm api alembic upgrade head
docker compose --profile dev run --rm api ruff check .
docker compose --profile dev run --rm api mypy src
docker compose --profile dev run --rm api pytest -q
docker compose --profile dev run --rm api job-agent eval run
docker compose --profile dev run --rm api job-agent release check
docker compose --profile dev down
```

Simple `make` or script targets may wrap these commands, but they may not run the
application toolchain directly on the host.

## Evidence required for a pass

Each milestone writes `artifacts/verification/milestone-NN.json` containing the
commit, UTC timestamp, image digest, commands, exit codes, test counts, and links
to relevant logs or screenshots. Evidence files must be generated from real
command results; handwritten success text is not evidence.

The final demo also requires:

- a clean-install log;
- an HTTP/browser smoke-test result;
- migration up/down/up evidence;
- an end-to-end persisted fixture result;
- one opt-in live read with a recorded current policy decision;
- one opt-in AI integration result with secrets scrubbed;
- an evaluation report with zero unsupported proposal claims;
- worker restart/idempotency evidence;
- backup and fresh-volume restore evidence;
- a final go/no-go report listing every known limitation.

## Automatic no-go conditions

These conditions fail the current acceptance attempt and must be repaired and
rerun. They are terminal `BLOCKED` conditions only when resolution requires
user-owned input/authority or an unresolved security, privacy, or compliance
decision.

- Any required service is a placeholder, fake success printer, or non-callable
  shell when the milestone requires an operational implementation.
- A readiness check reports healthy without checking its required dependencies.
- A command runs the Python application toolchain on the host.
- A test or evaluation silently substitutes a fake provider for a required opt-in
  integration test.
- A migration, release, policy, security, or backup/restore gate fails.
- A proposal contains an unsupported claim.
- A platform action lacks a current explicit allow decision.
- The working tree contains unexplained changes or milestone records disagree.
