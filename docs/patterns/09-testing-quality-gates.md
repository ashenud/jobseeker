# 09 - Testing and Quality Gates Pattern

- Repository-wide fast checks should include pytest, Ruff, mypy, and pre-commit once configured.
- Milestone checks listed in the milestone document are mandatory.
- Add tests with each functional vertical slice; do not weaken tests to make checks pass.
- Default tests must not call live paid APIs or uncontrolled external services.
- Recorded fixtures must be scrubbed of personal data and credentials.
- A milestone is not done until deliverables, docs, security/policy checks, and reproducible verification all pass.
