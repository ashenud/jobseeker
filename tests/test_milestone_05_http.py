from __future__ import annotations

from fastapi.testclient import TestClient

from job_agent.web.app import create_app
from job_agent.web.health import ComponentHealth


def client() -> TestClient:
    return TestClient(
        create_app(
            readiness_probe=lambda: ComponentHealth(database=True, redis=True)
        )
    )


def test_architecture_operation_returns_production_boundaries() -> None:
    response = client().get("/api/v1/architecture")
    assert response.status_code == 200
    body = response.json()
    assert body["style"] == "modular_monolith"
    modules = {module["name"]: module for module in body["modules"]}
    assert "workers" in modules
    assert "domain rules" in modules["workers"]["forbidden_responsibility"]
    assert "SubmissionConnector" in modules["workers"]["forbidden_responsibility"]


def test_state_machine_operation_is_derived_from_canonical_graph() -> None:
    response = client().get("/api/v1/state-machines")
    assert response.status_code == 200
    machines = {
        machine["machine"]: machine for machine in response.json()["state_machines"]
    }
    assert set(machines) == {"job", "proposal", "application"}
    assert machines["job"]["transitions"]["DISCOVERED"] == ["NORMALIZED"]
    assert machines["proposal"]["transitions"]["LOCKED_FOR_SUBMISSION"] == []
    assert set(machines["application"]["transitions"]["PACKAGE_PREPARED"]) == {
        "SUBMISSION_CANCELLED",
        "SUBMITTED_API",
        "SUBMITTED_MANUAL",
    }


def test_transition_validation_returns_typed_success() -> None:
    response = client().post(
        "/api/v1/transitions/validate",
        json={
            "current": {"machine": "job", "state": "DISCOVERED"},
            "target": {"machine": "job", "state": "NORMALIZED"},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "machine": "job",
        "current_state": "DISCOVERED",
        "target_state": "NORMALIZED",
    }


def test_transition_validation_has_stable_invalid_and_cross_machine_errors() -> None:
    invalid = client().post(
        "/api/v1/transitions/validate",
        json={
            "current": {"machine": "job", "state": "DISCOVERED"},
            "target": {"machine": "job", "state": "SCORED"},
        },
    )
    assert invalid.status_code == 409
    assert invalid.json()["error"]["code"] == "invalid_transition"

    cross_machine = client().post(
        "/api/v1/transitions/validate",
        json={
            "current": {"machine": "job", "state": "DISCOVERED"},
            "target": {"machine": "proposal", "state": "GENERATING"},
        },
    )
    assert cross_machine.status_code == 409
    assert cross_machine.json()["error"]["code"] == "cross_machine_transition"
    assert cross_machine.json()["error"]["target_machine"] == "proposal"


def test_unknown_state_error_is_stable_and_secret_free() -> None:
    response = client().post(
        "/api/v1/transitions/validate",
        json={
            "current": {"machine": "job", "state": "NOT_A_STATE"},
            "target": {"machine": "job", "state": "NORMALIZED"},
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unknown_state"


def test_operations_and_success_error_schemas_appear_in_openapi() -> None:
    schema = client().get("/openapi.json").json()
    paths = schema["paths"]
    assert "/api/v1/architecture" in paths
    assert "/api/v1/state-machines" in paths
    operation = paths["/api/v1/transitions/validate"]["post"]
    assert set(operation["responses"]) >= {"200", "400", "409", "422"}
    components = schema["components"]["schemas"]
    assert "TransitionValidationResponse" in components
    assert "TransitionErrorResponse" in components
