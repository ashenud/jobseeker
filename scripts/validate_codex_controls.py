"""Run deterministic negative checks for the repository Codex controls."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".codex" / "hooks" / "enforce_docker_boundary.py"


def load_hook():
    spec = importlib.util.spec_from_file_location("docker_boundary", HOOK)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {HOOK}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    hook = load_hook()
    cases = {
        "pytest -q": "pytest",
        "python -m pytest": "python",
        "docker run --rm job-agent pytest": "docker run",
    }
    for command, expected in cases.items():
        actual = hook.blocked_segment(command)
        if actual != expected:
            raise AssertionError(f"{command!r}: expected {expected!r}, got {actual!r}")
    for command in (
        "docker compose --profile dev run --rm api pytest -q",
        "docker compose --profile dev run --rm api python scripts/validate_docs.py",
        "git status --short",
    ):
        if hook.blocked_segment(command) is not None:
            raise AssertionError(f"allowed command was blocked: {command!r}")
    print("Codex control validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
