"""Retry-safe worker boundary for state commands."""

from __future__ import annotations

from job_agent.core.commands import TransitionCommand
from job_agent.core.contracts import TransitionResult
from job_agent.core.errors import ProtectedTransitionError
from job_agent.core.states import ApplicationState, JobState
from job_agent.core.transitions import TransitionExecutor


class RetryableTransitionHandler:
    """Delegates retries to the idempotent transition application service.

    The worker boundary intentionally has no submission connector and cannot
    produce external effects.
    """

    def __init__(self, transitions: TransitionExecutor) -> None:
        self._transitions = transitions

    def handle(self, command: TransitionCommand) -> TransitionResult:
        if command.target_state in {
            JobState.SUBMITTED_API,
            ApplicationState.SUBMITTED_API,
        }:
            raise ProtectedTransitionError(
                machine=command.aggregate_type,
                current_state=command.expected_state.value,
                target_state=command.target_state.value,
            )
        return self._transitions.execute(command)
