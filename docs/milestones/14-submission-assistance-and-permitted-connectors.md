# Milestone 14 - Submission Assistance and Permitted Connectors

## Goal

Bridge approved drafts to external platforms without turning the system into an unsafe auto-apply bot.

## Submission modes

### Mode A - Manual assist (default)

- Build a submission package.
- Show final proposal, rate, attachments, answers, and checklist.
- Copy proposal to clipboard.
- Open original job URL.
- User pastes, verifies, attaches files, and submits.
- User clicks `Mark submitted` and records timestamp/reference.

This mode works for Behance, Upwork without approved write API, Fiverr, LinkedIn, Contra, and unknown platforms.

### Mode B - Official API write with confirmation

Allowed only when:

1. current policy permits the exact write action;
2. official credentials and required scopes exist;
3. connector feature flag is enabled;
4. dry-run preview succeeds;
5. user issues a short-lived confirmation token for this exact application;
6. idempotency key prevents repeats;
7. API receipt is stored.

No scheduled or bulk confirmation is allowed.

### Mode C - Assisted browser form filling

Excluded from MVP. A later controlled browser extension may fill fields only after a user click and without evasion, but platform terms must be reviewed first. Playwright is for testing owned/local UI or explicitly permitted flows, not stealth marketplace automation.

## Submission package

- job/source identifiers;
- final locked proposal revision;
- rate/budget response;
- screening answers;
- selected portfolio links/attachments;
- source-specific warnings;
- required manual checklist;
- policy version;
- package checksum.

## Attachment selection

The agent may recommend portfolio projects but cannot attach unverified or client-confidential files. User confirms every attachment.

## Failure behavior

- Never retry a write blindly.
- Query official API status/receipt when possible.
- An ambiguous timeout becomes `SUBMISSION_UNKNOWN`, not automatic retry.
- Manual duplicate warning if an application already exists.

## Required deliverables

- submission package builder;
- clipboard/open-link manual flow;
- `Mark submitted` and `Cancel` actions;
- connector interface with dry-run;
- confirmation-token service;
- fake write connector for tests;
- no live write connector enabled by default.

## Codex execution prompt

```text
Implement Milestone 14 only. Build the default manual submission assistant and a generic confirmation-gated official API connector interface with a fake connector. Do not enable any real marketplace write action. Add idempotency, unknown-result handling, attachment checks, and tests proving approval alone cannot submit.
```

## Acceptance criteria

- [ ] Approved proposal can be copied and source opened.
- [ ] User must explicitly mark a manual submission.
- [ ] Approval and submission are separate commands.
- [ ] Write connectors require policy, feature flag, preview, confirmation, and idempotency.
- [ ] Ambiguous write results never auto-retry.
- [ ] No real write connector is enabled in default configuration.
