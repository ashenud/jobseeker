"""Retry-safe worker boundary for state commands."""

from __future__ import annotations

from job_agent.core.commands import TransitionCommand
from job_agent.core.contracts import TransitionResult
from job_agent.core.transitions import TransitionExecutor


class RetryableTransitionHandler:
    """Delegates retries to the idempotent transition application service.

    The worker boundary intentionally has no submission connector and cannot
    produce external effects.
    """

    def __init__(self, transitions: TransitionExecutor) -> None:
        self._transitions = transitions

    def handle(self, command: TransitionCommand) -> TransitionResult:
        return self._transitions.execute(command)
