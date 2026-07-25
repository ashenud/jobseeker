"""Application services that exclusively own state-transition transactions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable, Protocol
from uuid import UUID, uuid4

from job_agent.core.audit import AuditEvent
from job_agent.core.commands import TransitionCommand
from job_agent.core.contracts import TransitionResult, UnitOfWorkFactory
from job_agent.core.states import ProposalState, require_transition


class TransitionExecutor(Protocol):
    def execute(self, command: TransitionCommand) -> TransitionResult: ...


class TransitionApplicationService:
    def __init__(
        self,
        unit_of_work_factory: UnitOfWorkFactory,
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        event_id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._event_id_factory = event_id_factory

    def execute(self, command: TransitionCommand) -> TransitionResult:
        fingerprint = command.fingerprint()
        require_transition(command.expected_state, command.target_state)
        occurred_at = self._clock()
        event_id = self._event_id_factory()
        event = AuditEvent(
            event_id=event_id,
            event_type="state_transition",
            aggregate_type=command.aggregate_type,
            aggregate_id=command.aggregate_id,
            from_state=command.expected_state.value,
            to_state=command.target_state.value,
            actor=command.actor,
            reason=command.reason,
            correlation_id=command.correlation_id,
            idempotency_key=command.idempotency_key,
            occurred_at=occurred_at,
        )
        candidate = TransitionResult(
            aggregate_type=command.aggregate_type,
            aggregate_id=command.aggregate_id,
            previous_state=command.expected_state,
            current_state=command.target_state,
            audit_event_id=event_id,
            occurred_at=occurred_at,
            command_fingerprint=fingerprint,
        )
        with self._unit_of_work_factory() as unit_of_work:
            result = unit_of_work.transitions.apply_transition(command, event, candidate)
            unit_of_work.commit()
            return result


class ProposalApprovalService:
    """Approve reviewed content without any submission-connector dependency."""

    def __init__(self, transitions: TransitionExecutor) -> None:
        self._transitions = transitions

    def approve(self, command: TransitionCommand) -> TransitionResult:
        if (
            command.expected_state is not ProposalState.IN_REVIEW
            or command.target_state is not ProposalState.APPROVED
        ):
            raise ValueError("proposal approval requires IN_REVIEW -> APPROVED")
        return self._transitions.execute(command)
