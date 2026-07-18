# ADR 0001: Human-in-the-loop boundary

## Status

Accepted

## Context

The product goal is to help the owner find and respond to suitable freelance design work without creating an unsafe mass-bidding bot. Marketplace rules vary and may change. External communications, submissions, follow-ups, and account-affecting actions create reputational and account risk if performed without review.

## Decision

Human approval is a hard product boundary. By default, the system may discover, normalize, deduplicate, filter, score, draft, notify, and track work locally, but it must not communicate externally or submit proposals without explicit owner approval for the individual action.

Any future official API write connector must satisfy all of the following before it can perform an external action:

1. the platform policy registry explicitly permits the exact action and cites the permission source;
2. the connector has a disabled-by-default feature flag that the owner turns on;
3. the owner provides a per-action confirmation token or equivalent explicit confirmation; and
4. the action is audited with IDs, timestamps, decision state, and outcome.

`manual_only`, `disabled`, missing, stale, or unknown platform policy modes are hard blocks. The system will not include CAPTCHA solving, fingerprint spoofing, stealth plugins, hidden browser automation, proxy rotation intended to evade controls, rate-limit evasion, credential harvesting, cookie storage, or unattended bulk bidding.

## Consequences

- The MVP optimizes proposal quality, safety, and owner control over application volume.
- Some workflows remain slower than fully automated submission, but account and reputation risk is reduced.
- Later source adapters and submission helpers must enforce policy and approval state in code, not only in UI text.
- Tests must verify fail-closed behavior around platform policy and external actions.
