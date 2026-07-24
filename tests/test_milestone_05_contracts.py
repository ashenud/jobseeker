from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from job_agent.core.audit import AuditEvent
from job_agent.core.commands import TransitionCommand
from job_agent.core.contracts import TransitionResult
from job_agent.core.errors import (
    IdempotencyConflictError,
    InvalidTransitionError,
    StateConflictError,
    UnsafeAuditMetadataError,
)
from job_agent.core.states import JobState, MachineName, ProposalState
from job_agent.core.transitions import ProposalApprovalService, TransitionApplicationService
from job_agent.workers.transitions import RetryableTransitionHandler

AGGREGATE_ID = UUID("00000000-0000-0000-0000-000000000501")
CORRELATION_ID = UUID("00000000-0000-0000-0000-000000000502")
EVENT_ID = UUID("00000000-0000-0000-0000-000000000503")
NOW = datetime(2026, 7, 25, 10, 30, tzinfo=UTC)


class FakeTransitionRepository:
    def __init__(self, state: JobState | ProposalState) -> None:
        machine = (
            MachineName.JOB if isinstance(state, JobState) else MachineName.PROPOSAL
        )
        self.states = {(machine, AGGREGATE_ID): state}
        self.results: dict[tuple[MachineName, str], TransitionResult] = {}
        self.pending: tuple[TransitionCommand, AuditEvent, TransitionResult] | None = None
        self.audit_events: list[AuditEvent] = []

    def current_state(
        self, aggregate_type: MachineName, aggregate_id: UUID
    ) -> JobState | ProposalState | None:
        return self.states.get((aggregate_type, aggregate_id))

    def find_by_idempotency_key(
        self, aggregate_type: MachineName, idempotency_key: str
    ) -> TransitionResult | None:
        return self.results.get((aggregate_type, idempotency_key))

    def stage_state_and_audit(
        self,
        command: TransitionCommand,
        event: AuditEvent,
        result: TransitionResult,
    ) -> None:
        self.pending = (command, event, result)

    def commit_pending(self) -> None:
        assert self.pending is not None
        command, event, result = self.pending
        self.states[(command.aggregate_type, command.aggregate_id)] = result.current_state
        self.results[(command.aggregate_type, command.idempotency_key)] = result
        self.audit_events.append(event)
        self.pending = None


class FakeUnitOfWork:
    def __init__(self, repository: FakeTransitionRepository) -> None:
        self.transitions = repository
        self.commits = 0
        self.rollbacks = 0

    def __enter__(self) -> FakeUnitOfWork:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.transitions.commit_pending()
        self.commits += 1

    def rollback(self) -> None:
        self.transitions.pending = None
        self.rollbacks += 1


class FakeUnitOfWorkFactory:
    def __init__(self, repository: FakeTransitionRepository) -> None:
        self.repository = repository
        self.created: list[FakeUnitOfWork] = []

    def __call__(self) -> FakeUnitOfWork:
        unit_of_work = FakeUnitOfWork(self.repository)
        self.created.append(unit_of_work)
        return unit_of_work


class TransitionAndSubmissionSpy:
    """Expose both ports so tests detect accidental submission calls."""

    def __init__(self, transitions: TransitionApplicationService) -> None:
        self._transitions = transitions
        self.executed: list[TransitionCommand] = []
        self.submission_calls: list[object] = []

    def execute(self, transition: TransitionCommand) -> TransitionResult:
        self.executed.append(transition)
        return self._transitions.execute(transition)

    def submit(self, request: object) -> None:
        self.submission_calls.append(request)
        raise AssertionError("approval and transition retries must not submit")


def command(
    *,
    expected_state: JobState | ProposalState = JobState.DISCOVERED,
    target_state: JobState | ProposalState = JobState.NORMALIZED,
    idempotency_key: str = "transition-0501",
    reason: str = "normalized canonical source record",
) -> TransitionCommand:
    machine = (
        MachineName.JOB if isinstance(expected_state, JobState) else MachineName.PROPOSAL
    )
    return TransitionCommand(
        aggregate_type=machine,
        aggregate_id=AGGREGATE_ID,
        expected_state=expected_state,
        target_state=target_state,
        actor="normalization-service",
        reason=reason,
        correlation_id=CORRELATION_ID,
        idempotency_key=idempotency_key,
    )


def service(
    repository: FakeTransitionRepository,
) -> tuple[TransitionApplicationService, FakeUnitOfWorkFactory]:
    factory = FakeUnitOfWorkFactory(repository)
    return (
        TransitionApplicationService(
            factory,
            clock=lambda: NOW,
            event_id_factory=lambda: EVENT_ID,
        ),
        factory,
    )


def test_transition_atomically_commits_state_and_secret_free_audit() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, factory = service(repository)

    result = transitions.execute(command())

    assert result.current_state is JobState.NORMALIZED
    assert repository.states[(MachineName.JOB, AGGREGATE_ID)] is JobState.NORMALIZED
    assert repository.audit_events == [
        AuditEvent(
            event_id=EVENT_ID,
            event_type="state_transition",
            aggregate_type=MachineName.JOB,
            aggregate_id=AGGREGATE_ID,
            from_state="DISCOVERED",
            to_state="NORMALIZED",
            actor="normalization-service",
            reason="normalized canonical source record",
            correlation_id=CORRELATION_ID,
            idempotency_key="transition-0501",
            occurred_at=NOW,
        )
    ]
    assert factory.created[0].commits == 1


def test_expected_state_conflict_has_stable_error_and_no_commit() -> None:
    repository = FakeTransitionRepository(JobState.NORMALIZED)
    transitions, factory = service(repository)

    with pytest.raises(StateConflictError) as caught:
        transitions.execute(command())

    assert caught.value.code == "state_conflict"
    assert caught.value.actual_state == "NORMALIZED"
    assert not repository.audit_events
    assert factory.created[0].commits == 0


def test_invalid_transition_has_stable_error_and_no_staged_write() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, factory = service(repository)

    with pytest.raises(InvalidTransitionError) as caught:
        transitions.execute(command(target_state=JobState.SCORED))

    assert caught.value.code == "invalid_transition"
    assert repository.pending is None
    assert factory.created[0].rollbacks == 1


def test_idempotent_retry_returns_original_result_without_second_audit() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, _ = service(repository)

    original = transitions.execute(command())
    replay = transitions.execute(command())

    assert replay.replayed is True
    assert replay.audit_event_id == original.audit_event_id
    assert len(repository.audit_events) == 1


def test_reusing_idempotency_key_for_different_command_fails() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, _ = service(repository)
    transitions.execute(command())

    with pytest.raises(IdempotencyConflictError) as caught:
        transitions.execute(command(reason="different operation"))

    assert caught.value.code == "idempotency_conflict"
    assert len(repository.audit_events) == 1


def test_audit_metadata_rejects_likely_secrets_before_transaction() -> None:
    with pytest.raises(UnsafeAuditMetadataError):
        command(reason="api_key=do-not-store")


def test_proposal_approval_only_transitions_reviewed_revision() -> None:
    repository = FakeTransitionRepository(ProposalState.IN_REVIEW)
    transitions, _ = service(repository)
    boundary = TransitionAndSubmissionSpy(transitions)
    approval = ProposalApprovalService(boundary)

    result = approval.approve(
        command(
            expected_state=ProposalState.IN_REVIEW,
            target_state=ProposalState.APPROVED,
            idempotency_key="proposal-approval-0501",
            reason="owner approved reviewed revision",
        )
    )

    assert result.current_state is ProposalState.APPROVED
    assert len(boundary.executed) == 1
    assert boundary.submission_calls == []


def test_retryable_worker_replays_transition_without_external_calls() -> None:
    repository = FakeTransitionRepository(JobState.DISCOVERED)
    transitions, _ = service(repository)
    boundary = TransitionAndSubmissionSpy(transitions)
    worker = RetryableTransitionHandler(boundary)

    first = worker.handle(command())
    retry = worker.handle(command())

    assert first.current_state is JobState.NORMALIZED
    assert retry.replayed is True
    assert len(boundary.executed) == 2
    assert len(repository.audit_events) == 1
    assert boundary.submission_calls == []
