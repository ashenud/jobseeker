# 96 - Risk Register

| Risk | Likelihood | Impact | Controls | Owner signal |
|---|---|---|---|---|
| Marketplace account restriction | Medium | Critical | manual-first, policy registry, no stealth, no auto-write | policy/write audit |
| Proposal hallucination | Medium | High | verified evidence, claim ledger, blocker, evaluations | unsupported-claim metric |
| Source terms change | High over time | High | review dates, fail closed, stale/source-change alert | policy expiry |
| Duplicate submission | Low if controlled | Critical | separate approval/submission, idempotency, receipt | duplicate warning |
| LLM cost runaway | Medium | Medium | deterministic filters, hard budgets, one draft | cost ceiling |
| Private data leak | Low-Medium | High | local binding, redaction, private dirs, retention | security scans |
| Prompt injection | Medium | High | untrusted-data boundary, structured prompts, validators | adversarial eval |
| Source schema change | High over time | Medium | validation, fixture tests, circuit breaker | malformed/empty run |
| False negatives | Medium | Medium | archive low scores, pilot labels, calibration | missed-job review |
| Overengineering | Medium | Medium | modular monolith, milestone scope, ADR gate | dependency/repo review |
| PC sleep/offline | High | Medium | clear local limitation, startup/health alerts | source stale |
| Backup not restorable | Medium | High | scheduled restore test | restore report |
