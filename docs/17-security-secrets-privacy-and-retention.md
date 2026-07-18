# Milestone 17 - Security, Secrets, Privacy, and Retention

## Goal

Protect marketplace accounts, API keys, portfolio/client data, and the local host. The application has powerful access to job text and potentially external APIs, so security is a product feature.

## Threat model

Consider:

- malicious instructions embedded in job posts;
- XSS through source HTML;
- leaked API keys or Telegram tokens;
- unauthorized LAN access to the dashboard;
- accidental submission;
- dependency compromise;
- source payload containing personal data;
- sensitive data in logs/backups;
- database theft from a lost disk;
- prompt/response retention by providers;
- malicious attachments and links.

## Secret handling

- `.env` for development only, never committed.
- Prefer OS/secret-store integration later.
- Separate read and write API credentials when possible.
- Minimum scopes.
- Rotate and revoke documented.
- Redact secrets in logs and error traces.
- Configuration validation fails if production-like mode uses default secrets.

## Local network

- Bind to `127.0.0.1` by default.
- If LAN access is enabled, require authentication, CSRF protection, secure cookies, firewall restrictions, and an explicit warning.
- Do not expose PostgreSQL or Redis publicly.

## Content security

- sanitize all source HTML;
- render text by default;
- block remote images;
- safe external-link handling;
- validate file type and size;
- never execute downloaded content;
- no browser automation with stored sessions in MVP.

## LLM privacy

- send only fields needed for the task;
- remove contact details where unnecessary;
- configure provider storage settings where supported;
- keep request/response retention configurable;
- allow local/fake provider mode;
- delete derived embeddings with source records;
- do not send confidential portfolio documents by default.

## Retention defaults

Example:

- raw rejected jobs: 30 days;
- normalized jobs: 180 days;
- applications/outcomes: until user deletion;
- raw LLM responses: 30 days or disabled;
- audit metadata: 365 days;
- confirmation tokens: minutes;
- backups: rolling encrypted set.

The user can override, but deletion must cascade correctly.

## Required deliverables

- threat model;
- security settings and middleware;
- content sanitizer;
- secret redaction;
- retention/deletion jobs;
- data export/delete commands;
- dependency and container scanning scripts;
- security tests.

## Codex execution prompt

```text
Implement Milestone 17 only. Apply the documented threat model: localhost binding, auth option, CSRF, safe HTML, secret redaction, retention/deletion, provider data minimization, secure confirmation tokens, and dependency/container checks. Add security tests including malicious job HTML and prompt injection. Do not expose services to the LAN by default.
```

## Acceptance criteria

- [ ] Secrets do not appear in Git, logs, UI, or test artifacts.
- [ ] Malicious HTML and job instructions cannot execute or override system rules.
- [ ] Dashboard and services are local-only by default.
- [ ] Retention and deletion cover originals and derived data.
- [ ] Submission requires secure single-use confirmation when applicable.
- [ ] Backup/security procedures are documented.
