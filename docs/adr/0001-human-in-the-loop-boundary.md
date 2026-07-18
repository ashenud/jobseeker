# ADR 0001: Human-in-the-loop boundary

## Status

Proposed (revalidation)

## Context

External submissions, messages, follow-ups, and account-affecting actions create
reputational and platform risk. Marketplace rules differ and change. The product
must distinguish reviewing content from causing an external action.

## Decision

Approval is not transmission. Approving a proposal only locks the reviewed
revision and prepares a copy/open/manual-submit package. It never submits, sends,
messages, follows up, fills a remote form, or calls a write endpoint.

The MVP demo ends at manual owner submission: the owner leaves the application,
submits on the source platform, and returns to record the manual reference and
outcome. The demo includes no official write connector.

Missing, unknown, stale, `manual_only`, or `disabled` policy decisions block
network/write behavior before I/O. Behance and Upwork remain manual capture and
manual owner submission unless later current policy explicitly permits a narrower
action.

A future official write connector is outside this ADR's MVP authorization. It
would require a separately accepted scope, current documented permission for the
exact action, an owner-enabled feature flag, a single-use per-action confirmation
token, and an audit event with action ID, policy decision, timestamp, destination,
payload checksum, and outcome. Approval alone could satisfy none of those gates.

## Consequences

- Approval, package preparation, manual submission, and recorded outcome are
  separate auditable states.
- Retryable jobs and scheduled tasks cannot transmit approved content.
- Tests must prove approval causes zero external calls and tokens cannot be reused.
- CAPTCHA solving, credential/cookie capture, stealth, evasion, and unattended
  bulk bidding remain prohibited.
