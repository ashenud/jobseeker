# 09 - Testing and quality-gate pattern

Run all checks in Docker and keep four distinct layers:

1. Unit tests for pure rules, schemas, and state transitions.
2. Integration tests against PostgreSQL, pgvector, Redis, HTTP fakes, and Celery.
3. Browser/API E2E for the persisted user journey.
4. Separately tagged bounded live smokes for required permitted sources and AI.

Every acceptance criterion has a stable `MNN-ACNN` ID mapped to an observable
test/endpoint and recorded in the milestone receipt. Fakes are allowed in offline
tests but never satisfy a required live gate. Test counts must be nonzero.

The repository fast suite includes Ruff, mypy, pytest, documentation/status
validation, policy/security checks, and migration validation. Release adds full
E2E/evaluation, live integration receipts where required, clean-checkout Docker
reproduction, image scanning, and backup/restore.

Quality commands must fail nonzero when a threshold is intentionally breached.
Unconditional success printers, `ignore_errors`, empty test shells, and health
checks that bypass dependencies are release blockers.
