# Milestone 13 - Human Review Dashboard and Notifications

## Goal

Provide a fast local review queue where the owner can understand the job, score, evidence, proposal, risks, and next action without losing control.

## Primary UI

Use FastAPI + Jinja + HTMX/local JavaScript for the MVP. The dashboard binds to localhost and has a simple local authentication mechanism when enabled.

## Queue card

Show:

- source/platform and posting age;
- job title, client/company, budget, and location;
- overall score and dimension breakdown;
- deterministic filter results;
- red flags and missing data;
- retrieved portfolio evidence and links;
- proposal draft with inline edit;
- recommended attachment/project suggestions;
- actions: `Approve`, `Save edit`, `Skip`, `Need more info`, `Open source`;
- skip/edit reason capture.

## Review workflow

1. Job enters `IN_REVIEW`.
2. User reads source summary and evidence.
3. User edits if required; each save creates a proposal revision.
4. `Approve` validates policy, quality gates, and required fields again.
5. Approval creates a submission package, not an external submission.
6. Skip records a reason that feeds later scoring evaluation.

## Safe rendering

- Sanitize source HTML.
- Never execute scripts from postings.
- External links use clear source labels and safe target behavior.
- Avoid rendering remote images by default to reduce tracking.
- Escape all user/job content.

## Notifications

Optional Telegram notification may send a minimal summary and a local dashboard link. It must not expose full confidential content unless explicitly configured. Approval from Telegram is optional and should remain disabled initially; mobile edits are error-prone.

Alternative no-cloud notification: Windows toast or email to self.

## Accessibility and speed

- Keyboard shortcuts for next, approve, skip, and edit.
- Responsive enough for phone browser on the local network only if explicitly enabled.
- Clear color-independent status labels.
- Autosave drafts locally but require explicit approval.

## Required deliverables

- local dashboard routes/templates/assets;
- review service and transition commands;
- revision editor;
- notification provider interface;
- optional Telegram provider behind feature flag;
- UI and service tests.

## Codex execution prompt

```text
Implement Milestone 13 only. Build the localhost review dashboard with safe rendering, score/evidence visibility, inline proposal revisions, approve/skip/need-info actions, and an optional notification interface. Approval must only create a submission package. Do not send or submit anything externally.
```

## Acceptance criteria

- [ ] User can review and decide on a job in one screen.
- [ ] Every edit creates a revision and preserves prior text.
- [ ] Approval reruns policy and quality validation.
- [ ] No external action occurs on approval.
- [ ] Untrusted HTML/scripts cannot execute.
- [ ] Skip/edit reasons are captured for evaluation.
