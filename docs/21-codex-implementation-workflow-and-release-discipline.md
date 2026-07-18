# Milestone 21 - Codex Implementation Workflow and Release Discipline

## Goal

Make Codex a reliable implementation partner by controlling context, task size, review, tests, and repository state.

## Codex operating model

Codex reads `AGENTS.md` and works inside the repository. Give it one milestone at a time, a clean Git state, explicit verification commands, and permission boundaries. Do not ask it to “build everything” in one turn.

## Task loop

1. Create a branch `milestone/XX-short-name`.
2. Update status to `IN PROGRESS`.
3. Ask Codex to read the milestone and dependencies.
4. Request a plan and risk list before edits.
5. Approve or correct the plan.
6. Let Codex implement in small commits or one reviewable change.
7. Run milestone checks.
8. Ask Codex for a self-review focused on security, data integrity, policy, and tests.
9. Manually inspect diff and run the feature.
10. Update docs/status/changelog.
11. Tag milestone or merge.

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
- Keep milestone completion evidence in status/changelog.
- Do not paste the whole documentation set into every prompt.
- Ask Codex to cite repository files/lines in its plan.
- Start a new Codex thread when the context becomes confused or scope drifts.

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

## Codex execution prompt

```text
Implement Milestone 21 only. Review and strengthen the repository’s AGENTS.md, Codex prompt library, branch/commit/release workflow, self-review checklist, and milestone completion process. Add automation that checks status, tests, migrations, evaluation reports, and policy review dates before a release can be tagged.
```

## Acceptance criteria

- [ ] Codex can start any milestone from a clear prompt.
- [ ] Permanent instructions are concise and enforce boundaries.
- [ ] Release checks include policy, migrations, security, evaluations, and backup restore.
- [ ] The workflow prevents skipping milestones silently.
- [ ] User can review each change before continuing.
