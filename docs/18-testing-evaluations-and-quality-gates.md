# Milestone 18 - Testing, Evaluations, and Quality Gates

## Goal

Prove deterministic code and probabilistic LLM behavior are trustworthy enough for a real job-search workflow.

## Test pyramid

### Unit

- policy decisions;
- state transitions;
- parsers and currency/date logic;
- fingerprints and rules;
- schema validation;
- claim ledger;
- metric formulas.

### Integration

- database migrations/repositories;
- Redis/Celery task execution;
- adapter fixtures;
- OpenAI client mocked at HTTP boundary;
- pgvector retrieval;
- review and submission package flows.

### End-to-end

Fixture job -> ingest -> normalize -> rule -> score(fake) -> retrieve -> draft(fake) -> review -> approve -> copy/manual mark submitted -> CRM event.

No live marketplace submission test.

## LLM evaluation sets

Maintain versioned datasets for:

- packaging/label jobs;
- Amazon listing/A+ jobs;
- brand identity;
- 3D product visualization;
- architectural visualization;
- irrelevant jobs;
- low-budget/unrealistic scope;
- ambiguous jobs;
- adversarial prompt injection;
- concept-versus-completed-work evidence.

Each example includes expected score range, required red flags, relevant evidence IDs, forbidden claims, and proposal quality notes.

## Evaluation metrics

- score classification accuracy against human labels;
- calibration by score band;
- false-negative rate;
- evidence precision@k;
- unsupported claim count;
- proposal acceptance/light-edit rate;
- policy violation count;
- cost/latency percentiles.

A single “LLM judge” is not enough. Combine schema checks, deterministic validators, human labels, and optional model-based critique.

## Quality gates

Before merge:

```bash
make lint
make typecheck
make test
make test-integration
make eval-fast
```

Before release:

```bash
make db-migration-test
make e2e
make eval-full
make security-check
make backup-restore-test
```

Define thresholds in configuration and record evaluation versions.

## Required deliverables

- complete test commands;
- evaluation dataset format and starter set;
- evaluation runner and report;
- coverage thresholds focused on critical logic;
- CI configuration or local CI script;
- release quality gate.

## Codex execution prompt

```text
Implement Milestone 18 only. Build the test/evaluation framework and populate a representative private-safe dataset across the owner’s service categories and adversarial cases. Add deterministic and mocked end-to-end tests, score/evidence/proposal metrics, and release thresholds. No live paid or marketplace actions in default tests.
```

## Acceptance criteria

- [ ] Critical policy, submission, evidence, and state logic have strong tests.
- [ ] End-to-end fixture flow passes.
- [ ] Evaluation set covers relevant, irrelevant, risky, and adversarial jobs.
- [ ] Unsupported claim count must be zero for release.
- [ ] Thresholds and dataset versions are recorded.
- [ ] Tests are reproducible offline except explicitly tagged live tests.
