"""Exercise Milestone 05 operations through a running HTTP server."""

from __future__ import annotations

import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def request_json(
    base_url: str,
    path: str,
    *,
    payload: dict[str, object] | None = None,
) -> tuple[int, dict[str, object]]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data is not None else {},
        method="POST" if data is not None else "GET",
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    architecture_status, architecture = request_json(
        args.base_url, "/api/v1/architecture"
    )
    assert architecture_status == 200
    assert architecture["style"] == "modular_monolith"
    assert len(architecture["modules"]) >= 10  # type: ignore[arg-type]

    states_status, states = request_json(args.base_url, "/api/v1/state-machines")
    assert states_status == 200
    assert len(states["state_machines"]) == 3  # type: ignore[arg-type]

    valid_status, valid = request_json(
        args.base_url,
        "/api/v1/transitions/validate",
        payload={
            "current": {"machine": "job", "state": "DISCOVERED"},
            "target": {"machine": "job", "state": "NORMALIZED"},
        },
    )
    assert valid_status == 200
    assert valid["valid"] is True

    invalid_status, invalid = request_json(
        args.base_url,
        "/api/v1/transitions/validate",
        payload={
            "current": {"machine": "job", "state": "DISCOVERED"},
            "target": {"machine": "job", "state": "WON"},
        },
    )
    assert invalid_status == 409
    assert invalid["error"]["code"] == "invalid_transition"  # type: ignore[index]

    openapi_status, openapi = request_json(args.base_url, "/openapi.json")
    assert openapi_status == 200
    paths = openapi["paths"]
    assert "/api/v1/architecture" in paths  # type: ignore[operator]
    assert "/api/v1/state-machines" in paths  # type: ignore[operator]
    assert "/api/v1/transitions/validate" in paths  # type: ignore[operator]
    print("architecture HTTP/OpenAPI check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
