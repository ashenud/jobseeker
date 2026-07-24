#!/usr/bin/env python3
"""Require a real broker-backed Celery worker control reply."""

from __future__ import annotations

import json

from job_agent.workers.app import celery_app


def main() -> int:
    replies = celery_app.control.inspect(
        destination=["worker@worker"],
        timeout=10,
    ).ping()
    if not isinstance(replies, dict) or not replies:
        print("worker ping returned no replies")
        return 1
    if any(reply != {"ok": "pong"} for reply in replies.values()):
        print("worker ping returned an invalid reply")
        return 1
    print(json.dumps({"nodes": sorted(replies), "result": "pong"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
