"""Typed HTTP discovery and transition-validation operations."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from job_agent.core.architecture import DEPENDENCY_RULE, MODULE_BOUNDARIES
from job_agent.core.errors import CrossMachineTransitionError, InvalidTransitionError
from job_agent.core.states import (
    STATE_TYPES,
    TRANSITIONS,
    MachineName,
    parse_state,
    require_transition,
    terminal_states,
)
from job_agent.web.schemas import (
    ArchitectureResponse,
    ModuleBoundaryResponse,
    StateMachineResponse,
    StateMachinesResponse,
    TransitionErrorResponse,
    TransitionValidationRequest,
    TransitionValidationResponse,
)

router = APIRouter(prefix="/api/v1", tags=["architecture"])


@router.get("/architecture", response_model=ArchitectureResponse)
def architecture() -> ArchitectureResponse:
    return ArchitectureResponse(
        style="modular_monolith",
        dependency_rule=DEPENDENCY_RULE,
        modules=[
            ModuleBoundaryResponse(
                name=boundary.name,
                responsibility=boundary.responsibility,
                forbidden_responsibility=boundary.forbidden_responsibility,
                depends_on=list(boundary.depends_on),
            )
            for boundary in MODULE_BOUNDARIES
        ],
    )


@router.get("/state-machines", response_model=StateMachinesResponse)
def state_machines() -> StateMachinesResponse:
    machines: list[StateMachineResponse] = []
    for machine in MachineName:
        machines.append(
            StateMachineResponse(
                machine=machine,
                states=[state.value for state in STATE_TYPES[machine]],
                transitions={
                    state.value: sorted(target.value for target in targets)
                    for state, targets in TRANSITIONS[machine].items()
                },
                terminal_states=sorted(state.value for state in terminal_states(machine)),
            )
        )
    return StateMachinesResponse(state_machines=machines)


@router.post(
    "/transitions/validate",
    response_model=TransitionValidationResponse,
    responses={
        400: {"model": TransitionErrorResponse},
        409: {"model": TransitionErrorResponse},
    },
)
def validate_transition(
    request: TransitionValidationRequest,
) -> TransitionValidationResponse | JSONResponse:
    try:
        current = parse_state(request.current.machine, request.current.state)
        target = parse_state(request.target.machine, request.target.state)
    except ValueError:
        detail = {
            "code": "unknown_state",
            "message": "state is not defined for the specified machine",
            "machine": request.current.machine.value,
            "current_state": request.current.state,
            "target_state": request.target.state,
            "target_machine": request.target.machine.value,
        }
        return JSONResponse(status_code=400, content={"error": detail})

    try:
        require_transition(current, target)
    except (CrossMachineTransitionError, InvalidTransitionError) as error:
        return JSONResponse(status_code=409, content={"error": error.to_dict()})
    return TransitionValidationResponse(
        valid=True,
        machine=request.current.machine,
        current_state=current.value,
        target_state=target.value,
    )
