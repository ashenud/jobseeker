# 93 - Platform Connector Checklists

## Read/discovery connector approval

- [ ] Official terms/API/help page reviewed on a recorded date.
- [ ] Exact endpoint/feed documented.
- [ ] Authentication method and scopes documented.
- [ ] Rate limits and pagination documented.
- [ ] Storage/retention and attribution requirements documented.
- [ ] Personal data fields minimized.
- [ ] Policy action mode approved.
- [ ] Adapter uses timeouts, user agent, retries, and rate limiter.
- [ ] Sanitized fixtures exist.
- [ ] Live test is opt-in.
- [ ] Circuit breaker handles source changes.

## Write/submission connector approval

All read checks plus:

- [ ] Official write action explicitly permitted for this account/use.
- [ ] Separate write credential/scope where possible.
- [ ] User has approved risk.
- [ ] Feature disabled by default.
- [ ] Dry-run/preview exists.
- [ ] Single-use confirmation token required.
- [ ] Idempotency and receipt/status query implemented.
- [ ] Ambiguous timeout never blind-retries.
- [ ] Per-day cap and audit event implemented.
- [ ] Sandbox/test environment used if available.
- [ ] Manual fallback exists.

## Behance MVP checklist

- Use manual job capture.
- Open original job for user submission.
- Do not assume a public Jobs API.
- Revisit only after current official permission is documented.

## Upwork MVP checklist

- No scraping.
- Manual import unless approved official API credentials and scope exist.
- Submission remains manual by default.

## Freelancer MVP checklist

- Official API read connector may be considered.
- Review API terms and credentials.
- Bid endpoint remains disabled through pilot.

## Public feed checklist

- Verify feed ownership and current usage notes.
- Respect attribution and limits.
- Store only fields needed by the private workflow.
