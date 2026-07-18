# 05 - Configuration and Secrets Pattern

- Use Pydantic settings for environment variables and typed configuration loading.
- Version non-secret examples under `.env.example` and `config/*.example.yaml`.
- Keep local private configuration under ignored paths such as `data/private/`.
- Never store platform passwords, cookies, browser session tokens, payment details, or full inbox exports.
- Fail closed when configuration is missing, unknown, expired, or ambiguous.
- Every configurable model name, endpoint, threshold, schedule, policy mode, retention period, and cost limit must come from configuration.
