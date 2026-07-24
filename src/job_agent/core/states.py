"""Canonical aggregate state machines.

All state changes must be validated here and persisted through the transition
application service.  Modules must not maintain private transition tables.
"""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import TypeAlias

from job_agent.core.errors import CrossMachineTransitionError, InvalidTransitionError


class MachineName(StrEnum):
    JOB = "job"
    PROPOSAL = "proposal"
    APPLICATION = "application"


class JobState(StrEnum):
    DISCOVERED = "DISCOVERED"
    NORMALIZED = "NORMALIZED"
    DUPLICATE = "DUPLICATE"
    RULE_REJECTED = "RULE_REJECTED"
    READY_TO_SCORE = "READY_TO_SCORE"
    SCORED = "SCORED"
    SCORE_FAILED = "SCORE_FAILED"
    LOW_FIT = "LOW_FIT"
    READY_TO_DRAFT = "READY_TO_DRAFT"
    DRAFTED = "DRAFTED"
    DRAFT_FAILED = "DRAFT_FAILED"
    IN_REVIEW = "IN_REVIEW"
    SKIPPED = "SKIPPED"
    NEEDS_EDIT = "NEEDS_EDIT"
    APPROVED = "APPROVED"
    READY_TO_SUBMIT = "READY_TO_SUBMIT"
    SUBMITTED_MANUAL = "SUBMITTED_MANUAL"
    SUBMITTED_API = "SUBMITTED_API"
    SUBMISSION_CANCELLED = "SUBMISSION_CANCELLED"
    REPLIED = "REPLIED"
    INTERVIEW = "INTERVIEW"
    WON = "WON"
    LOST = "LOST"
    WITHDRAWN = "WITHDRAWN"


class ProposalState(StrEnum):
    GENERATING = "GENERATING"
    GENERATED = "GENERATED"
    VALIDATING = "VALIDATING"
    VALID = "VALID"
    INVALID = "INVALID"
    IN_REVIEW = "IN_REVIEW"
    EDITED = "EDITED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    LOCKED_FOR_SUBMISSION = "LOCKED_FOR_SUBMISSION"


class ApplicationState(StrEnum):
    READY_TO_PREPARE = "READY_TO_PREPARE"
    PACKAGE_PREPARED = "PACKAGE_PREPARED"
    SUBMISSION_CANCELLED = "SUBMISSION_CANCELLED"
    SUBMITTED_MANUAL = "SUBMITTED_MANUAL"
    SUBMITTED_API = "SUBMITTED_API"
    REPLIED = "REPLIED"
    INTERVIEW = "INTERVIEW"
    WON = "WON"
    LOST = "LOST"
    WITHDRAWN = "WITHDRAWN"


MachineState: TypeAlias = JobState | ProposalState | ApplicationState

_JOB_TRANSITIONS: dict[MachineState, frozenset[MachineState]] = {
    JobState.DISCOVERED: frozenset({JobState.NORMALIZED}),
    JobState.NORMALIZED: frozenset(
        {JobState.DUPLICATE, JobState.RULE_REJECTED, JobState.READY_TO_SCORE}
    ),
    JobState.DUPLICATE: frozenset(),
    JobState.RULE_REJECTED: frozenset(),
    JobState.READY_TO_SCORE: frozenset({JobState.SCORED, JobState.SCORE_FAILED}),
    JobState.SCORED: frozenset({JobState.LOW_FIT, JobState.READY_TO_DRAFT}),
    JobState.SCORE_FAILED: frozenset(),
    JobState.LOW_FIT: frozenset(),
    JobState.READY_TO_DRAFT: frozenset({JobState.DRAFTED, JobState.DRAFT_FAILED}),
    JobState.DRAFTED: frozenset({JobState.IN_REVIEW}),
    JobState.DRAFT_FAILED: frozenset(),
    JobState.IN_REVIEW: frozenset(
        {JobState.SKIPPED, JobState.NEEDS_EDIT, JobState.APPROVED}
    ),
    JobState.SKIPPED: frozenset(),
    JobState.NEEDS_EDIT: frozenset(),
    JobState.APPROVED: frozenset({JobState.READY_TO_SUBMIT}),
    JobState.READY_TO_SUBMIT: frozenset(
        {
            JobState.SUBMITTED_MANUAL,
            JobState.SUBMITTED_API,
            JobState.SUBMISSION_CANCELLED,
        }
    ),
    JobState.SUBMITTED_MANUAL: frozenset(
        {
            JobState.REPLIED,
            JobState.INTERVIEW,
            JobState.WON,
            JobState.LOST,
            JobState.WITHDRAWN,
        }
    ),
    JobState.SUBMITTED_API: frozenset(
        {
            JobState.REPLIED,
            JobState.INTERVIEW,
            JobState.WON,
            JobState.LOST,
            JobState.WITHDRAWN,
        }
    ),
    JobState.SUBMISSION_CANCELLED: frozenset(),
    JobState.REPLIED: frozenset(
        {JobState.INTERVIEW, JobState.WON, JobState.LOST, JobState.WITHDRAWN}
    ),
    JobState.INTERVIEW: frozenset({JobState.WON, JobState.LOST, JobState.WITHDRAWN}),
    JobState.WON: frozenset(),
    JobState.LOST: frozenset(),
    JobState.WITHDRAWN: frozenset(),
}

_PROPOSAL_TRANSITIONS: dict[MachineState, frozenset[MachineState]] = {
    ProposalState.GENERATING: frozenset({ProposalState.GENERATED}),
    ProposalState.GENERATED: frozenset({ProposalState.VALIDATING}),
    ProposalState.VALIDATING: frozenset({ProposalState.VALID, ProposalState.INVALID}),
    ProposalState.VALID: frozenset({ProposalState.IN_REVIEW}),
    ProposalState.INVALID: frozenset(),
    ProposalState.IN_REVIEW: frozenset(
        {ProposalState.EDITED, ProposalState.APPROVED, ProposalState.REJECTED}
    ),
    ProposalState.EDITED: frozenset(),
    ProposalState.APPROVED: frozenset({ProposalState.LOCKED_FOR_SUBMISSION}),
    ProposalState.REJECTED: frozenset(),
    ProposalState.LOCKED_FOR_SUBMISSION: frozenset(),
}

_APPLICATION_TRANSITIONS: dict[MachineState, frozenset[MachineState]] = {
    ApplicationState.READY_TO_PREPARE: frozenset({ApplicationState.PACKAGE_PREPARED}),
    ApplicationState.PACKAGE_PREPARED: frozenset(
        {
            ApplicationState.SUBMISSION_CANCELLED,
            ApplicationState.SUBMITTED_MANUAL,
            ApplicationState.SUBMITTED_API,
        }
    ),
    ApplicationState.SUBMISSION_CANCELLED: frozenset(),
    ApplicationState.SUBMITTED_MANUAL: frozenset(
        {
            ApplicationState.REPLIED,
            ApplicationState.INTERVIEW,
            ApplicationState.WON,
            ApplicationState.LOST,
            ApplicationState.WITHDRAWN,
        }
    ),
    ApplicationState.SUBMITTED_API: frozenset(
        {
            ApplicationState.REPLIED,
            ApplicationState.INTERVIEW,
            ApplicationState.WON,
            ApplicationState.LOST,
            ApplicationState.WITHDRAWN,
        }
    ),
    ApplicationState.REPLIED: frozenset(
        {
            ApplicationState.INTERVIEW,
            ApplicationState.WON,
            ApplicationState.LOST,
            ApplicationState.WITHDRAWN,
        }
    ),
    ApplicationState.INTERVIEW: frozenset(
        {ApplicationState.WON, ApplicationState.LOST, ApplicationState.WITHDRAWN}
    ),
    ApplicationState.WON: frozenset(),
    ApplicationState.LOST: frozenset(),
    ApplicationState.WITHDRAWN: frozenset(),
}

TRANSITIONS = MappingProxyType(
    {
        MachineName.JOB: MappingProxyType(_JOB_TRANSITIONS),
        MachineName.PROPOSAL: MappingProxyType(_PROPOSAL_TRANSITIONS),
        MachineName.APPLICATION: MappingProxyType(_APPLICATION_TRANSITIONS),
    }
)

STATE_TYPES: dict[MachineName, type[MachineState]] = {
    MachineName.JOB: JobState,
    MachineName.PROPOSAL: ProposalState,
    MachineName.APPLICATION: ApplicationState,
}


def machine_for_state(state: MachineState) -> MachineName:
    if isinstance(state, JobState):
        return MachineName.JOB
    if isinstance(state, ProposalState):
        return MachineName.PROPOSAL
    return MachineName.APPLICATION


def parse_state(machine: MachineName, value: str) -> MachineState:
    return STATE_TYPES[machine](value)


def can_transition(current: MachineState, target: MachineState) -> bool:
    if type(current) is not type(target):
        return False
    return target in TRANSITIONS[machine_for_state(current)][current]


def require_transition(current: MachineState, target: MachineState) -> None:
    source_machine = machine_for_state(current)
    target_machine = machine_for_state(target)
    if source_machine is not target_machine:
        raise CrossMachineTransitionError(
            machine=source_machine,
            current_state=current.value,
            target_state=target.value,
            target_machine=target_machine,
        )
    if not can_transition(current, target):
        raise InvalidTransitionError(
            machine=source_machine,
            current_state=current.value,
            target_state=target.value,
        )


def terminal_states(machine: MachineName) -> frozenset[MachineState]:
    return frozenset(
        state for state, targets in TRANSITIONS[machine].items() if not targets
    )
