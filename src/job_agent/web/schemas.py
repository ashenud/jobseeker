"""Public schemas for architecture and transition discovery."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from job_agent.core.states import MachineName


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModuleBoundaryResponse(ApiModel):
    name: str
    responsibility: str
    forbidden_responsibility: str
    depends_on: list[str]


class ArchitectureResponse(ApiModel):
    style: Literal["modular_monolith"]
    dependency_rule: str
    modules: list[ModuleBoundaryResponse]


class StateMachineResponse(ApiModel):
    machine: MachineName
    states: list[str]
    transitions: dict[str, list[str]]
    terminal_states: list[str]


class StateMachinesResponse(ApiModel):
    state_machines: list[StateMachineResponse]


class StateReference(ApiModel):
    machine: MachineName
    state: str


class TransitionValidationRequest(ApiModel):
    current: StateReference
    target: StateReference


class TransitionValidationResponse(ApiModel):
    valid: Literal[True]
    machine: MachineName
    current_state: str
    target_state: str


class TransitionErrorDetail(ApiModel):
    code: str
    message: str
    machine: str
    current_state: str | None
    target_state: str | None
    target_machine: str | None = None


class TransitionErrorResponse(ApiModel):
    error: TransitionErrorDetail
