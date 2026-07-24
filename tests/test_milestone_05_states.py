from __future__ import annotations

from itertools import product

import pytest

from job_agent.core.errors import CrossMachineTransitionError, InvalidTransitionError
from job_agent.core.states import (
    ApplicationState,
    JobState,
    MachineName,
    ProposalState,
    can_transition,
    require_transition,
    terminal_states,
)

EXPECTED_JOB_EDGES = {
    ("DISCOVERED", "NORMALIZED"),
    ("NORMALIZED", "DUPLICATE"),
    ("NORMALIZED", "RULE_REJECTED"),
    ("NORMALIZED", "READY_TO_SCORE"),
    ("READY_TO_SCORE", "SCORED"),
    ("READY_TO_SCORE", "SCORE_FAILED"),
    ("SCORED", "LOW_FIT"),
    ("SCORED", "READY_TO_DRAFT"),
    ("READY_TO_DRAFT", "DRAFTED"),
    ("READY_TO_DRAFT", "DRAFT_FAILED"),
    ("DRAFTED", "IN_REVIEW"),
    ("IN_REVIEW", "SKIPPED"),
    ("IN_REVIEW", "NEEDS_EDIT"),
    ("IN_REVIEW", "APPROVED"),
    ("APPROVED", "READY_TO_SUBMIT"),
    ("READY_TO_SUBMIT", "SUBMITTED_MANUAL"),
    ("READY_TO_SUBMIT", "SUBMITTED_API"),
    ("READY_TO_SUBMIT", "SUBMISSION_CANCELLED"),
    *{
        (submitted, outcome)
        for submitted in ("SUBMITTED_MANUAL", "SUBMITTED_API")
        for outcome in ("REPLIED", "INTERVIEW", "WON", "LOST", "WITHDRAWN")
    },
    ("REPLIED", "INTERVIEW"),
    ("REPLIED", "WON"),
    ("REPLIED", "LOST"),
    ("REPLIED", "WITHDRAWN"),
    ("INTERVIEW", "WON"),
    ("INTERVIEW", "LOST"),
    ("INTERVIEW", "WITHDRAWN"),
}

EXPECTED_PROPOSAL_EDGES = {
    ("GENERATING", "GENERATED"),
    ("GENERATED", "VALIDATING"),
    ("VALIDATING", "VALID"),
    ("VALIDATING", "INVALID"),
    ("VALID", "IN_REVIEW"),
    ("IN_REVIEW", "EDITED"),
    ("IN_REVIEW", "APPROVED"),
    ("IN_REVIEW", "REJECTED"),
    ("APPROVED", "LOCKED_FOR_SUBMISSION"),
}

EXPECTED_APPLICATION_EDGES = {
    ("READY_TO_PREPARE", "PACKAGE_PREPARED"),
    ("PACKAGE_PREPARED", "SUBMISSION_CANCELLED"),
    ("PACKAGE_PREPARED", "SUBMITTED_MANUAL"),
    ("PACKAGE_PREPARED", "SUBMITTED_API"),
    *{
        (submitted, outcome)
        for submitted in ("SUBMITTED_MANUAL", "SUBMITTED_API")
        for outcome in ("REPLIED", "INTERVIEW", "WON", "LOST", "WITHDRAWN")
    },
    ("REPLIED", "INTERVIEW"),
    ("REPLIED", "WON"),
    ("REPLIED", "LOST"),
    ("REPLIED", "WITHDRAWN"),
    ("INTERVIEW", "WON"),
    ("INTERVIEW", "LOST"),
    ("INTERVIEW", "WITHDRAWN"),
}


@pytest.mark.parametrize(
    ("state_type", "expected_names", "expected_edges"),
    [
        (
            JobState,
            {
                "DISCOVERED",
                "NORMALIZED",
                "DUPLICATE",
                "RULE_REJECTED",
                "READY_TO_SCORE",
                "SCORED",
                "SCORE_FAILED",
                "LOW_FIT",
                "READY_TO_DRAFT",
                "DRAFTED",
                "DRAFT_FAILED",
                "IN_REVIEW",
                "SKIPPED",
                "NEEDS_EDIT",
                "APPROVED",
                "READY_TO_SUBMIT",
                "SUBMITTED_MANUAL",
                "SUBMITTED_API",
                "SUBMISSION_CANCELLED",
                "REPLIED",
                "INTERVIEW",
                "WON",
                "LOST",
                "WITHDRAWN",
            },
            EXPECTED_JOB_EDGES,
        ),
        (
            ProposalState,
            {
                "GENERATING",
                "GENERATED",
                "VALIDATING",
                "VALID",
                "INVALID",
                "IN_REVIEW",
                "EDITED",
                "APPROVED",
                "REJECTED",
                "LOCKED_FOR_SUBMISSION",
            },
            EXPECTED_PROPOSAL_EDGES,
        ),
        (
            ApplicationState,
            {
                "READY_TO_PREPARE",
                "PACKAGE_PREPARED",
                "SUBMISSION_CANCELLED",
                "SUBMITTED_MANUAL",
                "SUBMITTED_API",
                "REPLIED",
                "INTERVIEW",
                "WON",
                "LOST",
                "WITHDRAWN",
            },
            EXPECTED_APPLICATION_EDGES,
        ),
    ],
)
def test_complete_allowed_and_forbidden_edge_matrix(
    state_type: type[JobState] | type[ProposalState] | type[ApplicationState],
    expected_names: set[str],
    expected_edges: set[tuple[str, str]],
) -> None:
    states = tuple(state_type)
    assert {state.value for state in states} == expected_names
    for current, target in product(states, repeat=2):
        expected = (current.value, target.value) in expected_edges
        assert can_transition(current, target) is expected
        if expected:
            require_transition(current, target)
        else:
            with pytest.raises(InvalidTransitionError):
                require_transition(current, target)


def test_cross_machine_attempts_are_always_forbidden() -> None:
    state_groups = (tuple(JobState), tuple(ProposalState), tuple(ApplicationState))
    for source_index, source_group in enumerate(state_groups):
        for target_index, target_group in enumerate(state_groups):
            if source_index == target_index:
                continue
            for current, target in product(source_group, target_group):
                assert not can_transition(current, target)
                with pytest.raises(CrossMachineTransitionError):
                    require_transition(current, target)


@pytest.mark.parametrize(
    ("machine", "expected"),
    [
        (
            MachineName.JOB,
            {
                "DUPLICATE",
                "RULE_REJECTED",
                "SCORE_FAILED",
                "LOW_FIT",
                "DRAFT_FAILED",
                "SKIPPED",
                "NEEDS_EDIT",
                "SUBMISSION_CANCELLED",
                "WON",
                "LOST",
                "WITHDRAWN",
            },
        ),
        (
            MachineName.PROPOSAL,
            {"INVALID", "EDITED", "REJECTED", "LOCKED_FOR_SUBMISSION"},
        ),
        (
            MachineName.APPLICATION,
            {"SUBMISSION_CANCELLED", "WON", "LOST", "WITHDRAWN"},
        ),
    ],
)
def test_terminal_state_sets_are_exact(machine: MachineName, expected: set[str]) -> None:
    assert {state.value for state in terminal_states(machine)} == expected


def test_locked_proposal_revision_cannot_be_edited_in_place() -> None:
    assert not can_transition(
        ProposalState.LOCKED_FOR_SUBMISSION, ProposalState.EDITED
    )
    with pytest.raises(InvalidTransitionError):
        require_transition(
            ProposalState.LOCKED_FOR_SUBMISSION, ProposalState.EDITED
        )
