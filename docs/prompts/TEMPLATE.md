# Milestone prompt template

Numbered prompts are thin entry points. The reusable procedure lives in
`$jobseeker-milestone`; the milestone owns requirements and acceptance.

Every numbered prompt must identify:

1. milestone ID/title and exact dependency statuses;
2. legacy implementation gaps that must be replaced;
3. required milestone, pattern, ADR, schema, and reference reads;
4. production deliverables and explicit non-goals;
5. stable acceptance IDs mapped to observable behavior and tests;
6. exact Docker Compose build/start/migrate/test/smoke/teardown commands;
7. whether a bounded real connector or AI smoke is mandatory;
8. named subagent assignments with non-overlapping ownership;
9. placeholder and silent-fallback prohibitions;
10. evidence receipt, independent review, clean-checkout reproduction, commits,
    status transitions, and stop-on-failure behavior.

Test doubles may exist only in test/fixture paths or explicitly selected offline
configuration. A required real integration may never silently fall back to one.
