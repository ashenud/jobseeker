# Milestone 21 - Codex Implementation Workflow and Release Discipline

## Recovery gate

Exercise—not merely document—the repo `AGENTS.md`, `$jobseeker-milestone` skill,
named agents, hooks, command rules, documentation validator, evidence validator,
and release handoff. Negative tests must prove skipped dependencies, direct host
toolchain commands, dirty/missing evidence, stale policy, failed evaluation,
broken migration, and failed restore cannot produce `DONE` or a release pass.

The selected Codex surfaces follow the current official documentation for
[customization and AGENTS.md](https://developers.openai.com/codex/concepts/customization),
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[hooks](https://learn.chatgpt.com/docs/hooks), and
[configuration](https://developers.openai.com/codex/config-reference). Project
configuration must use only documented keys; repository rules and evidence
validators provide the product-specific enforcement.

## Goal

Make Codex a reliable implementation partner by controlling context, task size, review, tests, and repository state.

## Codex operating model

Use each current Codex surface for its documented scope:

- `AGENTS.md` for concise durable repository rules;
- `$jobseeker-milestone` under `.agents/skills/` for the reusable workflow;
- `.codex/agents/*.toml` for bounded planner, explorer, worker, analyst, and
  independent reviewer roles;
- `.codex/config.toml` for documented project settings and agent limits;
- `.codex/hooks.json` for lightweight lifecycle guardrails;
- `.codex/rules/*.rules` for destructive-command escalation policy;
- a persistent Codex Goal for continuity only when the user requests the full
  multi-milestone run;
- Docker validators and CI as the authoritative enforcement boundary.

## Task loop

1. Select the only `READY` milestone and verify dependencies.
2. Plan acceptance-to-test mappings with a read-only planner/explorer.
3. Implement a bounded vertical slice with explicit file ownership.
4. Create the implementation commit.
5. Run Docker gates and clean-checkout reproduction against that commit.
6. Generate a machine-readable evidence receipt.
7. Obtain independent test and policy/release reviews.
8. Resolve findings and rerun affected gates.
9. Commit status/changelog/evidence only after `GO`.
10. Advance automatically only when the next dependency is ready.

## Prompt shape

A strong instruction contains:

- exact milestone;
- files to read;
- scope and forbidden scope;
- required deliverables;
- verification commands;
- expected final report;
- instruction not to hide failures.

Use the templates in `docs/92-codex-prompt-library.md`.

## Context discipline

- Put permanent rules in `AGENTS.md`.
- Keep current decisions in ADRs.
- Keep machine-readable milestone evidence under `artifacts/verification/` and
  progress only in `IMPLEMENTATION_STATUS.md`.
- Do not paste the whole documentation set into every prompt.
- Ask Codex to cite repository files/lines in its plan.
- Use subagents to isolate noisy exploration/test output and compact/fresh context
  when the coordinating thread becomes noisy.

## Review checklist

Before accepting Codex output:

- Does code match the current milestone only?
- Are platform/policy checks fail-closed?
- Are secrets or personal data exposed?
- Are migrations safe?
- Are network calls timed out and tested?
- Are LLM outputs validated?
- Are writes idempotent?
- Are docs and examples executable?
- Did Codex weaken tests to make them pass?
- Did it introduce unnecessary dependencies?

## Release discipline

- Semantic versioning after pilot.
- Conventional changelog entries.
- Tagged releases.
- Migration revision recorded.
- Evaluation report attached to release.
- Backup/restore test before release.
- No release when policy review is expired or unsupported claims appear.

## Required deliverables

- final `AGENTS.md` review;
- Codex prompt templates;
- branch/commit/release conventions;
- pull-request/self-review template;
- milestone completion script/checklist;
- release checklist.


## Acceptance criteria

- [ ] Codex can start any milestone from a clear prompt.
- [ ] Permanent instructions are concise and enforce boundaries.
- [ ] Release checks include policy, migrations, security, evaluations, and backup restore.
- [ ] The workflow prevents skipping milestones silently.
- [ ] Independent agents review each milestone before autonomous continuation.
- [ ] Hooks and validators reject direct host toolchain commands and evidence-free `DONE` states.
