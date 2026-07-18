# 07 - Background Jobs Pattern

- Use Redis and Celery for background work and schedules.
- Every task must have an idempotency key or equivalent duplicate-suppression strategy.
- External I/O must use timeouts, bounded retries with jitter, bounded concurrency, and clear terminal failure states.
- Background tasks should record start/end timestamps, attempt counts, result summaries, and safe error details.
- Periodic jobs must be configurable and disabled by default until the relevant milestone enables them.
- Avoid runaway LLM or source calls by enforcing per-run and daily budgets.
