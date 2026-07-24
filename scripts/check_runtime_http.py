#!/usr/bin/env python3
"""Validate the running Uvicorn HTTP boundary without exposing configuration."""

from __future__ import annotations

import argparse
import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen


def get_json(url: str) -> tuple[int, dict[str, Any]]:
    try:
        response = urlopen(url, timeout=8)
    except HTTPError as exc:
        response = exc
    with response:
        status = response.status
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{url} did not return a JSON object")
    return status, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument(
        "--expected-readiness",
        choices=("ready", "database-down", "redis-down"),
        required=True,
    )
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    live_status, live = get_json(f"{base_url}/health/live")
    ready_status, ready = get_json(f"{base_url}/health/ready")
    version_status, version = get_json(f"{base_url}/version")
    if live_status != 200 or live != {"status": "live"}:
        raise ValueError("liveness response is invalid")
    if version_status != 200 or version.get("commit") != args.expected_commit:
        raise ValueError("version response does not identify the tested commit")
    if not isinstance(version.get("version"), str) or not version["version"]:
        raise ValueError("version response lacks the application version")

    expected_components = {"database": "up", "redis": "up"}
    expected_status = 200
    expected_label = "ready"
    if args.expected_readiness == "database-down":
        expected_components["database"] = "down"
        expected_status = 503
        expected_label = "not_ready"
    elif args.expected_readiness == "redis-down":
        expected_components["redis"] = "down"
        expected_status = 503
        expected_label = "not_ready"
    expected_ready = {"status": expected_label, "components": expected_components}
    if ready_status != expected_status or ready != expected_ready:
        raise ValueError("readiness response does not match dependency state")

    print(
        json.dumps(
            {
                "commit": version["commit"],
                "liveness": live["status"],
                "readiness": ready,
                "version": version["version"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
