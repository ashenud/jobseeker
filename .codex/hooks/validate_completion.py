#!/usr/bin/env python3
"""Block a turn from ending with missing or incomplete DONE evidence."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys
from types import ModuleType


DONE_ROW = re.compile(r"^\|\s*(\d{2})\s*\|.*\|\s*DONE\s*\|", re.MULTILINE)
ROOT_MARKERS = ("IMPLEMENTATION_STATUS.md", "scripts/validate_milestone.py")


def repository_root(
    payload_cwd: Path | None = None,
    hook_path: Path = Path(__file__),
) -> Path:
    """Resolve the repository from the installed hook, never solely from payload cwd."""
    resolved_hook = hook_path.resolve()
    candidates = [resolved_hook.parents[2]]
    if payload_cwd is not None:
        resolved_cwd = payload_cwd.resolve()
        candidates.extend((resolved_cwd, *resolved_cwd.parents))
    for candidate in candidates:
        if all((candidate / marker).is_file() for marker in ROOT_MARKERS):
            return candidate
    # Returning the hook-owned location fails closed: incomplete_done reports a
    # missing validator instead of silently inspecting an unrelated directory.
    return resolved_hook.parents[2]


def _load_validator(root: Path) -> ModuleType:
    path = root / "scripts" / "validate_milestone.py"
    spec = importlib.util.spec_from_file_location("milestone_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def incomplete_done(root: Path) -> list[str]:
    """Return schema errors for every milestone currently marked DONE."""
    status = root / "IMPLEMENTATION_STATUS.md"
    if not status.is_file():
        return []
    done = DONE_ROW.findall(status.read_text(encoding="utf-8"))
    if not done:
        return []
    try:
        validator = _load_validator(root)
    except (OSError, RuntimeError) as exc:
        return [str(exc)]
    errors: list[str] = []
    for number in done:
        errors.extend(validator.validate_receipt(number, root))
    return errors


def main() -> int:
    payload_cwd: Path | None = None
    try:
        payload = json.load(sys.stdin)
        if isinstance(payload, dict) and payload.get("cwd"):
            payload_cwd = Path(str(payload["cwd"]))
    except (json.JSONDecodeError, OSError):
        payload_cwd = Path.cwd()
    root = repository_root(payload_cwd)
    errors = incomplete_done(root)
    if errors:
        result = {
            "decision": "block",
            "reason": (
                "Milestones marked DONE have missing or incomplete verification evidence: "
                + "; ".join(errors)
                + ". Restore an honest state or generate validated evidence from real Docker results."
            ),
        }
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
