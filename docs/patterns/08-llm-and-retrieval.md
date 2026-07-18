# 08 - LLM and Retrieval Pattern

- Apply deterministic rules before LLM calls.
- Use provider-neutral interfaces for LLMs and embeddings.
- Require structured model output validated with Pydantic or JSON Schema.
- Every proposal claim must map to an evidence record; unsupported claims block approval.
- Keep confidential user/client data out of prompts unless explicitly needed and allowed by configuration.
- Tests must not call live paid APIs by default; use fixtures and fake providers for default checks.
- Track prompt versions, model configuration, token/cost estimates, and validation failures.
