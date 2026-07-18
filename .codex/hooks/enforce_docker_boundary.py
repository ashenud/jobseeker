#!/usr/bin/env python3
"""Deny host-native application toolchain commands before Codex runs them."""

from __future__ import annotations

import json
import re
import sys


DENIED = {
    "alembic",
    "celery",
    "job-agent",
    "mypy",
    "pip",
    "pip3",
    "pre-commit",
    "pytest",
    "python",
    "python3",
    "ruff",
    "uvicorn",
}
SHELLS = {"bash", "sh", "zsh"}


def executable(segment: str) -> str:
    words = segment.strip().split()
    while words and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", words[0]):
        words.pop(0)
    return words[0] if words else ""


def blocked_segment(segment: str) -> str | None:
    command = executable(segment)
    if command == "docker":
        words = segment.strip().split()
        # Docker control-plane inspection is allowed, but application processes
        # must use the repository's Compose services so profiles, env, volumes,
        # and network policy remain reproducible.
        if len(words) > 1 and words[1] in {"run", "exec"}:
            return "docker " + words[1]
        return None
    if command == "docker-compose":
        if re.match(r"docker-compose\s+(run|exec)\b", segment.strip()):
            return command
        return None
    if command in DENIED:
        return command
    if command == "uv" and re.search(r"\buv\s+(run|sync|lock|pip)\b", segment):
        return "uv"
    if command in SHELLS and any(re.search(rf"\b{re.escape(tool)}\b", segment) for tool in DENIED):
        return command
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or tool_input.get("cmd") or "")
    for segment in re.split(r"(?:&&|\|\||[;|])", command):
        denied = blocked_segment(segment)
        if denied:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"Host-native '{denied}' is blocked. Run application builds, "
                        "dependencies, Python, tests, migrations, and checks through "
                        "docker compose."
                    ),
                }
            }
            print(json.dumps(result))
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
