# Milestone 01 - Project Charter and Scope

## Recovery gate

Milestone 00 must be `DONE`. The prior charter and ADRs are unaccepted inputs
until this milestone proves alignment with `docs/DEMO_ACCEPTANCE.md`, the
assisted-submission boundary, conditional integration authority, Docker-only
execution, measurable safety outcomes, and frozen downstream decisions.

## Goal

Freeze a realistic local MVP: permitted opportunity intelligence and
evidence-grounded proposal preparation with owner review and manual owner
submission. It is not a scraper, messaging bot, universal auto-apply service, or
authorization for any named integration.

## Required deliverables

- `docs/PROJECT_CHARTER.md`
- `docs/adr/0001-human-in-the-loop-boundary.md`
- `docs/adr/0002-local-first-mvp.md`
- an aligned `README.md` product and execution summary
- executable M01 semantics in `scripts/validate_docs.py` with focused negative
  tests

The coordinator records changelog delivery and accepts ADR status only after
Docker gates, evidence, clean reproduction, and independent review pass.

## Frozen scope

- Approval prepares and locks content; it never transmits. The demo ends with the
  owner submitting manually and recording the reference.
- No official write connector is included in the MVP demo.
- Manual capture is required. Jobicy RSS/API and Remote OK JSON/RSS are conditional
  live-read goals. OpenAI Responses API structured output is a conditional,
  opt-in real-AI goal.
- Naming a goal grants no permission, credential, spend, endpoint, model, scrape,
  or write authority. Milestones 02, 08, and 10 own those decisions and stop
  fail-closed when required inputs are absent.
- Behance and Upwork remain manual unless a later current policy explicitly
  permits a narrower action.
- Application and toolchain work executes in Docker Compose containers. The host
  is limited to Git, Docker/Compose, file inspection, Codex controls, and thin
  Docker wrappers.
- The measurable hard targets are zero duplicate normalized jobs after repeat
  ingestion, zero unsupported claims, and zero unapproved external actions.

## Acceptance-to-test map

| Stable ID | Observable acceptance | Docker evidence |
|---|---|---|
| **M01-AC01** | The charter contains the ordered browser-visible demo journey from clean start through manual submission, persistence, release checks, and restore; it defines zero duplicates, unsupported claims, and unapproved actions. | `python scripts/validate_docs.py` and focused charter tests in `pytest -q` |
| **M01-AC02** | Charter, ADR 0001, and README separate approval, preparation, and manual owner submission; name conditional source/AI goals without granting authority; exclude official writes from the demo. | Semantic validator, negative permission/approval tests, and independent policy review |
| **M01-AC03** | Charter, ADR 0002, prompt, and README consistently require Docker-only application/toolchain/runtime execution and the local-first host boundary. | Semantic validator, negative Docker-scope tests, and clean-checkout Docker reproduction |
| **M01-AC04** | Prompt dependency is 00 and includes the demo contract; downstream decisions are frozen with M02/M08/M10 authoritative; both ADRs remain proposed until evidence; no owner scope decision is unresolved. | Semantic validator, negative dependency/unresolved-decision tests, receipt mapping, and reviewer `GO` |

Each acceptance entry in `artifacts/verification/milestone-01.json` records a
`PASS` only from real command logs and reviewer references.

## Stop condition

Do not begin Milestone 02 if any charter semantic check, Docker gate, clean
reproduction, evidence mapping, or independent review fails. A missing permission,
credential, current policy, endpoint/model selection, private evidence input, or
budget blocks its owning downstream milestone; it never broadens this charter.
