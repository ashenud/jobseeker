# 02 - Python Project Standards

- Target Python 3.12 unless an ADR changes the baseline.
- Use typed public functions, small modules, and explicit domain boundaries.
- Never wrap imports in `try`/`except`; missing optional dependencies should be represented by configuration or adapter registration.
- Use UTC internally and convert to local time only at the UI boundary.
- Use UUIDs for internal entities and stable source fingerprints for deduplication.
- Keep provider-neutral interfaces for sources, LLMs, embeddings, notifications, storage, and submission assistance.
- Do not hardcode model names, URLs, thresholds, credentials, or platform behavior in application code.
