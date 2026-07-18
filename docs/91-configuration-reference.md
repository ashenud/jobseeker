# 91 - Configuration Reference

## Configuration layers

1. Code defaults: safe and disabled.
2. Versioned non-secret YAML under `config/`.
3. Local private YAML under `data/private/`.
4. Environment variables for secrets and deployment overrides.
5. Database runtime settings only for user-adjustable values with audit history.

Precedence: environment/private overrides versioned configuration, but no override may grant an action prohibited by code or an expired platform policy.

## Files

- `profile.yaml` - identity, services, evidence claims, rates, exclusions, tone.
- `scoring.yaml` - rule weights, thresholds, dimensions, daily caps.
- `sources.yaml` - enabled adapters, schedules, query parameters.
- `platform_policy.yaml` - legal/operational authorization.
- `notifications.yaml` - local/Telegram settings without token.
- `retention.yaml` - data lifetimes.
- `models.yaml` - provider/model names, cost assumptions, timeouts.

## Required safety defaults

```yaml
submission:
  api_write_enabled: false
  browser_fill_enabled: false
  confirmation_ttl_seconds: 300
outreach:
  sending_enabled: false
network:
  bind_host: 127.0.0.1
llm:
  enabled: false
  daily_cost_limit_usd: 1.00
```

## Validation

- Unknown keys are errors in production-like mode.
- Currency codes use ISO values.
- Time zones use IANA names.
- Thresholds remain within valid range.
- A source cannot be enabled without a current platform policy record.
- A write connector cannot be enabled without explicit action permission.
