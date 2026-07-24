# Success metrics

The executable KPI definitions live under `metrics` in `config/scoring.yaml`.
Each definition has a stable ID, strict calculation operation, explicit numerator
and denominator, human-readable formula, zero-denominator behavior, data sources,
cadence, and conservative pilot target. The profile bundle validator rejects
missing, unknown, or duplicate definitions.

The operations have deterministic runtime semantics:

- `numerator_count` requires a finite, non-negative integral scalar and returns
  that count independently of the denominator;
- `ratio` divides the numerator by the denominator;
- `percentage` divides and multiplies by 100, rejecting a numerator greater than
  its denominator;
- `median` computes the median of the supplied numerator observations and requires
  the denominator to equal their count.

All inputs must be finite and non-negative. For ratio, percentage, and median
operations, a zero denominator returns `0.0` for `zero` or `None` for
`not_available`; no operation divides by zero. A `numerator_count` always
preserves its validated numerator, including when the supplied denominator is
zero, so nonzero safety violations cannot be hidden. For example, eight
unsupported claims with denominator zero evaluates to `8.0`, 12 relevant jobs
across three discovery days evaluates to `4.0`, four relevant reviews out of
five evaluates to `80.0`, and review times of 1, 5, 2, and 3 minutes evaluate to
a median of `2.5`.

The profile, scoring, and portfolio-manifest schemas currently support exactly
version `1.0`; unknown or mixed bundle versions fail closed.

The pilot emphasizes quality and control rather than volume:

- reviewed-job relevance is at least 80%;
- at least 60% of reviewed drafts require only light edits;
- unsupported proposal claims remain exactly zero;
- unauthorized external actions remain exactly zero;
- median discovery-to-review time is at most two minutes;
- surfaced and submitted volume, replies, interviews, offers, and wins are counted;
- response and win rates are grouped by platform and service;
- LLM cost per reviewed job and per reply is measured;
- false positives remain at or below 20%;
- reply, win, cost, and owner factuality-trust metrics establish baselines.

Rates must be segmented later by platform and service when sufficient observations
exist. Each metric declares whether a zero denominator reports `not_available` or
the numeric value `zero`.

Validate the profile, scoring rules, evidence manifest, and KPIs together with:

```bash
docker compose --profile dev run --rm --no-deps api job-agent profile-validate
```

The command prints only a sanitized summary: schema versions, aggregate counts,
and issue categories. Configuration failures do not expose file contents,
portfolio text, local paths, or validation internals.
